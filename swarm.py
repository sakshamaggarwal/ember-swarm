#!/usr/bin/env python3
import argparse,json,os,sys,time,urllib.request,urllib.error
from concurrent.futures import ThreadPoolExecutor,as_completed

API_URL="https://openrouter.ai/api/v1/chat/completions"
MODEL="meta/muse-ember"
EXPERTS=["Architect","Biologist","Psychologist","Mechanical Engineer","Economist","Urban Planner","Nutritionist","Materials Scientist","Sociologist","Doctor","Electrical Engineer","Environmental Scientist","Historian","Philosopher","Data Scientist","Security Expert","Logistics Manager","Teacher","Artist","Farmer","Chemist","Geologist","Astronomer","Communications Expert","Lawyer","Energy Engineer","Robotics Engineer","Software Developer","Anthropologist","Diplomat","Geneticist","Neuroscientist","Ethicist","Game Designer","Musician","Chef","Firefighter","Waste Management Expert","Climatologist","Pharmacist","Civil Engineer","Aerospace Engineer","Linguist","Statistician","Librarian","Nurse","Veterinarian","Meteorologist","Oceanographer","Toxicologist","Epidemiologist","Therapist","Social Worker","Behavioral Economist","Supply Chain Manager","Landscape Architect","Microbiologist","Physicist","Mathematician","Cryptographer","Network Engineer","UX Designer","Product Manager","Journalist","Filmmaker","Botanist","Zoologist","Archaeologist","Cartographer","Seismologist","Hydrologist","Renewable Energy Specialist","Nanotechnologist","Biomedical Engineer","Ergonomist","Transportation Planner","Demographer","Futurist","Ethics Board Member","Military Strategist","Disaster Response Expert","Child Development Specialist","Geriatrician","Sports Scientist","Mediator","Patent Attorney","Venture Capitalist","QA Engineer","Sustainability Consultant","Acoustician","Color Theorist","Textile Engineer","Food Scientist","Sleep Researcher","Happiness Researcher","Behavioral Scientist","Urban Ecologist","Waste-to-Energy Specialist","Space Psychologist","Xenobiologist"]
ti=0;to=0;done=0

def call(msgs,key):
    body=json.dumps({"model":MODEL,"messages":msgs,"max_tokens":400}).encode()
    req=urllib.request.Request(API_URL,data=body,headers={"Authorization":f"Bearer {key}","Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req,timeout=120) as r:
            d=json.loads(r.read())
    except urllib.error.HTTPError as e:
        return None,f"HTTP {e.code}: {e.read().decode()[:200]}"
    except Exception as e:
        return None,str(e)[:200]
    if d.get("error"): return None,f"Error: {json.dumps(d['error'])[:200]}"
    return {"content":d["choices"][0]["message"]["content"],"usage":d.get("usage",{})},None

def agent(key,expert,q,total):
    global ti,to,done
    msgs=[{"role":"system","content":f"You are a {expert}. Give your most creative, specific, actionable answer. Be concise (150-250 words). Focus on ideas only a {expert} would think of."},{"role":"user","content":q}]
    r,err=call(msgs,key)
    done+=1
    if r: ti+=r["usage"].get("prompt_tokens",0); to+=r["usage"].get("completion_tokens",0)
    cost=(ti*0.10+to*0.50)/1e6
    print(f"\r  [{'#'*(done*30//total)}{'.'*(30-done*30//total)}] {done}/{total}  ${cost:.4f}",end="",flush=True)
    if err: return {"expert":expert,"answer":f"[error: {err}]","tokens":0}
    return {"expert":expert,"answer":r["content"],"tokens":r["usage"].get("prompt_tokens",0)+r["usage"].get("completion_tokens",0)}

def synth(key,q,answers):
    block="\n\n".join(f"**{a['expert']}:** {a['answer']}" for a in answers if not a["answer"].startswith("[err"))
    msgs=[{"role":"system","content":"You are a brilliant synthesizer. Combine the best ideas from all experts into one coherent plan. Organize by theme. Be specific. 500-800 words."},{"role":"user","content":f"QUESTION: {q}\n\nEXPERT ANSWERS:\n{block}"}]
    r,err=call(msgs,key)
    if err: return f"[Error: {err}]",{}
    return r["content"],r.get("usage",{})

def judge(key,q,s,n):
    msgs=[{"role":"system","content":f"You are Judge #{n}. Score on CREATIVITY, FEASIBILITY, COMPLETENESS (each 1-10). Format: CREATIVITY: X/10 - reason\nFEASIBILITY: X/10 - reason\nCOMPLETENESS: X/10 - reason"},{"role":"user","content":f"QUESTION: {q}\n\nSYNTHESIS:\n{s}"}]
    r,err=call(msgs,key)
    if err: return f"[Error: {err}]",{}
    return r["content"],r.get("usage",{})

def html(q,answers,synthesis,judgments,ci):
    good=[a for a in answers if not a["answer"].startswith("[err")]
    cards="".join(f'<div class="c"><b style="color:#f78166">{a["expert"]}</b><p>{a["answer"]}</p><small>{a["tokens"]}tok</small></div>' for a in good)
    jds="".join(f'<div class="j">{j}</div>' for j in judgments)
    return f'<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Ember Swarm</title><style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,sans-serif;background:#0d1117;color:#e6edf3;padding:2rem;max-width:1200px;margin:0 auto}}h1{{color:#f78166;font-size:2rem}}h2{{color:#3fb950;margin:2rem 0 1rem}}.sub{{color:#8b949e;margin-bottom:2rem}}.stats{{display:flex;gap:1.5rem;flex-wrap:wrap;margin:1.5rem 0}}.s{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem 1.5rem}}.sv{{font-size:1.8rem;font-weight:bold;color:#f78166}}.sl{{color:#8b949e;font-size:.85rem}}.syn{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1.5rem;line-height:1.7;white-space:pre-wrap}}.gr{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem}}.c{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem}}.c p{{font-size:.9rem;line-height:1.5;margin:.5rem 0}}.c small{{color:#8b949e}}.j{{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:1rem;margin:.5rem 0;white-space:pre-wrap}}</style></head><body><h1>Ember Swarm</h1><p class="sub">"{q}"</p><div class="stats"><div class="s"><div class="sv">{ci["a"]}</div><div class="sl">Agents</div></div><div class="s"><div class="sv">${ci["c"]:.4f}</div><div class="sl">Total Cost</div></div><div class="s"><div class="sv">{ci["t"]:,}</div><div class="sl">Tokens</div></div><div class="s"><div class="sv">{ci["d"]:.1f}s</div><div class="sl">Wall Time</div></div></div><h2>Synthesized Plan</h2><div class="syn">{synthesis}</div><h2>Judge Scores</h2>{jds}<h2>All {ci["a"]} Expert Answers</h2><div class="gr">{cards}</div><div style="color:#8b949e;margin-top:3rem;padding-top:1rem;border-top:1px solid #30363d;font-size:.85rem">Built with Muse Ember via OpenRouter | Ember Swarm | OpenRouter x Meta Build Day Nov 2026</div></body></html>'

def main():
    global ti,to,done
    p=argparse.ArgumentParser()
    p.add_argument("question")
    p.add_argument("--agents",type=int,default=100)
    p.add_argument("--save",default="report.html")
    a=p.parse_args()
    key=os.environ.get("OPENROUTER_API_KEY")
    if not key: sys.exit("Set OPENROUTER_API_KEY first: export OPENROUTER_API_KEY=sk-or-v1-...")
    experts=EXPERTS[:a.agents]
    print(f"\n  Ember Swarm\n  Q: {a.question}\n  Agents: {a.agents} | Model: {MODEL}\n")
    print("  Phase 1: Swarm...")
    t0=time.time()
    with ThreadPoolExecutor(max_workers=20) as pool:
        answers=[f.result() for f in as_completed({pool.submit(agent,key,e,a.question,a.agents):e for e in experts})]
    good=[x for x in answers if not x["answer"].startswith("[err")]
    print(f"\n  {len(good)} answers in {time.time()-t0:.1f}s\n\n  Phase 2: Synthesize...")
    synthesis,su=synth(key,a.question,good)
    ti+=su.get("prompt_tokens",0);to+=su.get("completion_tokens",0)
    print("  Done\n\n  Phase 3: Judge...")
    judgments=[]
    with ThreadPoolExecutor(max_workers=10) as pool:
        for c,u in [f.result() for f in as_completed([pool.submit(judge,key,a.question,synthesis,i+1) for i in range(10)])]:
            judgments.append(c);ti+=u.get("prompt_tokens",0);to+=u.get("completion_tokens",0)
    tt=time.time()-t0;cost=(ti*0.10+to*0.50)/1e6;tok=ti+to
    print(f"  Done\n\n  ===== RESULTS =====\n  Cost: ${cost:.4f}\n  Tokens: {tok:,}\n  Time: {tt:.1f}s\n  Agents: {a.agents}+1+10\n  ====================\n")
    print("  PLAN:\n");print(synthesis);print("\n  SCORES:\n")
    for j in judgments: print(j);print()
    with open(a.save,"w") as f: f.write(html(a.question,answers,synthesis,judgments,{"a":a.agents,"c":cost,"t":tok,"d":tt}))
    print(f"  Report: {a.save}\n  Run: open {a.save}\n")

if __name__=="__main__": main()

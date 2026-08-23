import json
import httpx
from typing import Dict, Any, List
from app.core.config import settings
from app.core.logging import logger

def ask_finops_assistant(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    q_lower = question.lower()
    intent = 'GENERAL_FINOPS'
    if any(k in q_lower for k in ['why', 'high', 'bill', 'expensive', 'costly', 'increase', 'surge', 'spend']):
        intent = 'COST_ANALYSIS'
    elif any(k in q_lower for k in ['idle', 'waste', 'save', 'saving', 'recommend', 'reduce', 'cut', 'opportunity']):
        intent = 'SAVINGS_RECOMMENDATIONS'
    elif any(k in q_lower for k in ['health', 'score', 'grade', 'status']):
        intent = 'HEALTH_SCORE'
    elif any(k in q_lower for k in ['budget', 'limit', 'exceed', 'threshold']):
        intent = 'BUDGETS'
    elif any(k in q_lower for k in ['storage', 's3', 'ebs', 'snapshot']):
        intent = 'STORAGE_OPTIMIZATION'
    elif any(k in q_lower for k in ['ec2', 'compute', 'server', 'instance']):
        intent = 'COMPUTE_OPTIMIZATION'

    if settings.LLM_PROVIDER in ['gemini', 'openai'] and settings.LLM_API_KEY:
        try:
            return _call_external_llm(question, context, intent)
        except Exception as e:
            logger.warning(f"External LLM call failed: {e}")

    answer = _generate_grounded_response(question, context, intent)
    followups = [
        "How can I optimize our RDS databases?",
        "What are the top 3 idle resources incurring waste?",
        "Are we projected to exceed our monthly AWS budget?"
    ]
    return {
        'question': question,
        'answer': answer,
        'intent': intent,
        'factual_context': context,
        'suggested_followups': followups
    }

def _generate_grounded_response(question: str, context: Dict[str, Any], intent: str) -> str:
    acc_name = context.get('account_name', 'your AWS account')
    curr_spend = context.get('current_month_spend', 0.0)
    savings = context.get('potential_monthly_savings', 0.0)
    score = context.get('cloud_health_score', 80)
    grade = context.get('cloud_health_grade', 'B')
    top_svcs = context.get('top_services', [])
    recs = context.get('recommendations', [])
    anoms = context.get('recent_anomalies', [])

    if intent == 'COST_ANALYSIS':
        svc_parts = [f"**{s['service']}** (${s['amount']:,.2f})" for s in top_svcs[:3]]
        top_svc_str = ', '.join(svc_parts) if svc_parts else 'No spend recorded'
        anom_str = ''
        if anoms:
            anom_str = f"\n\n**Notable Cost Surge**: Detected a **{anoms[0]['deviation']}** surge on {anoms[0]['service']} on {anoms[0]['date']}."
        return (
            f"For **{acc_name}**, current month spend is **${curr_spend:,.2f}**.\n\n"
            f"The primary cost drivers are: {top_svc_str}.{anom_str}\n\n"
            f"You have **${savings:,.2f}/month** in identified potential savings opportunities that can immediately reduce your run rate."
        )

    elif intent == 'SAVINGS_RECOMMENDATIONS':
        rec_bullets = '\n'.join([f"- **{r['title']}** ({r['category']}): Estimated potential savings of **${r['monthly_savings']:,.2f}/mo**.\n  *Evidence*: {r['evidence']}" for r in recs[:4]])
        return (
            f"We have identified **${savings:,.2f}/month** (${savings * 12:,.2f}/year) in potential optimization savings across **{len(recs)} active recommendations**:\n\n"
            f"{rec_bullets}\n\n"
            f"All recommendations are advisory - review before making infrastructure changes."
        )

    elif intent == 'HEALTH_SCORE':
        exps = '\n'.join([f"- {e}" for e in context.get('health_explanations', [])])
        return (
            f"Your **Cloud Health Score is {score}/100 (Grade: {grade})**.\n\n"
            f"**Breakdown & Key Drivers**:\n{exps}\n\n"
            f"Addressing the {len(recs)} active recommendations can raise your health score to **95+ (Grade A)**."
        )

    elif intent == 'BUDGETS':
        budgets = context.get('budgets', [])
        b_str = ', '.join([f"{b['name']} (${b['amount']:,.2f}/{b['period']})" for b in budgets]) if budgets else 'No active budgets configured.'
        return (
            f"**Budget Status for {acc_name}**:\n\n"
            f"Current spend this month: **${curr_spend:,.2f}**.\n"
            f"Active Budgets: {b_str}.\n\n"
            f"Tip: Set up automated 50%, 75%, 90%, and 100% threshold alerts in the Budgets section to prevent month-end surprises."
        )

    elif intent == 'STORAGE_OPTIMIZATION':
        storage_recs = [r for r in recs if 'Storage' in r['category'] or 'Snapshot' in r['category'] or 'S3' in r['title'] or 'EBS' in r['title']]
        s_bullets = '\n'.join([f"- **{r['title']}**: Save **${r['monthly_savings']:,.2f}/mo** ({r['evidence']})" for r in storage_recs]) if storage_recs else 'No urgent storage waste detected.'
        return (
            f"**Storage FinOps Recommendations**:\n\n"
            f"{s_bullets}\n\n"
            f"**Best Practice**: Ensure EBS snapshots over 60 days old are pruned, unattached volumes are deleted, and large S3 buckets use S3 Lifecycle rules transitioning to Intelligent-Tiering or Glacier."
        )

    else:
        return (
            f"**Smart Cloud Cost Guardian Intelligence for {acc_name}**:\n\n"
            f"- **Current Spend**: ${curr_spend:,.2f} this month\n"
            f"- **Identified Savings**: ${savings:,.2f}/month (${savings * 12:,.2f}/year)\n"
            f"- **Cloud Health Score**: {score}/100 (Grade {grade})\n"
            f"- **Active Recommendations**: {len(recs)} optimization opportunities\n\n"
            f"Ask me anything about your EC2 instances, RDS databases, S3 storage, budgets, or specific anomalies!"
        )

def _call_external_llm(question: str, context: Dict[str, Any], intent: str) -> Dict[str, Any]:
    prompt = f"""You are Smart Cloud Cost Guardian AI, an expert FinOps and AWS Cloud Architect.
You must answer the user question accurately using ONLY the factual AWS data provided below.
Never hallucinate resources or costs. Clearly state estimates vs actual billing.

FACTUAL AWS CONTEXT:
{json.dumps(context, indent=2)}

USER QUESTION:
{question}
"""
    if settings.LLM_PROVIDER == 'gemini':
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.LLM_MODEL}:generateContent?key={settings.LLM_API_KEY}"
        payload = {'contents': [{'parts': [{'text': prompt}]}]}
        with httpx.Client(timeout=15.0) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                text = data['candidates'][0]['content']['parts'][0]['text']
                return {
                    'question': question,
                    'answer': text,
                    'intent': intent,
                    'factual_context': context,
                    'suggested_followups': ['How can I cut my EC2 costs?', 'Explain my health score.']
                }
    return {'question': question, 'answer': _generate_grounded_response(question, context, intent), 'intent': intent, 'factual_context': context, 'suggested_followups': []}

import json
import csv
import re

def get_data_classification_score(value):
    """Calculate score based on data classification."""
    mapping = {
        'Red - Highly Confidential': 5,
        'Orange - Confidential': 4,
        'Yellow - Internal': 2,
        'Green - Public': 0
    }
    return mapping.get(value, 0)

def get_business_criticality_score(value):
    """Calculate score based on business criticality."""
    mapping = {
        'Business critical': 5,
        '1 - Mission Critical': 5,
        '2 - Critical': 4,
        'Important': 3,
        '3 - Important': 3,
        'Standard': 0,
        '4 - Non-Critical': 0
    }
    return mapping.get(value, 0)

def get_emergency_tier_score(value):
    """Calculate score based on emergency tier (lower hours = higher score)."""
    if not value: return 0
    val_str = str(value).lower()
    
    if 'critical' in val_str: return 3
        
    try:
        hours_match = re.search(r'(\d+)\s*hour', val_str)
        if hours_match:
            hours = int(hours_match.group(1))
            if hours <= 2: return 3
            if hours <= 12: return 2
            if hours <= 24: return 1
            return 0
    except:
        pass
    return 0

def get_disaster_recovery_rto_score(value):
    """Calculate score based on disaster recovery RTO."""
    if not value: return 2
    value_str = str(value).strip().lower()
    
    if value_str == 'immediate': return 6
    if value_str == 'undetermined': return 2
    
    try:
        hours = 0
        if 'week' in value_str:
            match = re.search(r'(\d+)', value_str)
            hours = int(match.group(1)) * 168 if match else 168
        elif 'month' in value_str:
            match = re.search(r'(\d+)', value_str)
            hours = int(match.group(1)) * 720 if match else 720
        else:
            match = re.search(r'(\d+)', value_str)
            hours = int(match.group(1)) if match else 24

        if hours == 0: return 6
        elif hours < 4: return 5
        elif hours <= 8: return 4
        elif hours <= 24: return 3
        elif hours <= 72: return 2
        elif hours <= 168: return 1
        else: return 0
    except:
        return 2

def get_disaster_recovery_rpo_score(value):
    """Calculate score based on disaster recovery RPO."""
    if not value: return 2
    value_str = str(value).strip().lower()
    if value_str == 'yes': return 4
    if value_str == 'no': return 0
    return get_disaster_recovery_rto_score(value)

def get_userbase_score(external_users, internal_users):
    """Calculate score based on total user base."""
    total = 0
    def parse_users(val):
        try: return int(str(val).replace(',', ''))
        except (ValueError, TypeError): return 0

    total += parse_users(external_users)
    total += parse_users(internal_users)
    
    if total >= 20000: return 7
    elif total >= 10000: return 5
    elif total >= 5000: return 3
    elif total >= 500: return 2
    elif total >= 100: return 1
    else: return 0

def get_external_users_score(value):
    mapping = {'Yes': 5, 'No': 0}
    return mapping.get(value, 0)

def get_external_facing_score(value):
    mapping = {'Yes': 5, 'No': 0}
    return mapping.get(value, 1)

def get_waf_enabled_score(value):
    mapping = {'Yes': 0, 'No': 1}
    return mapping.get(value, 1)

def get_ring_fenced_score(value):
    mapping = {'Yes': 0, 'No': 1}
    return mapping.get(value, 1)

def get_eol_score(value):
    mapping = {'Yes': 3, 'No': 0}
    return mapping.get(value, 1)

def get_security_issues_score(value):
    try:
        issues = int(value)
        if issues >= 2: return 2
        elif issues == 1: return 1
        else: return 0
    except (ValueError, TypeError):
        return 0

def get_app_security_classification_score(value):
    if value is None: return 2
    mapping = {
        'Critical': 4, 'D': 4, 'F': 4,
        'High': 3,     'C': 3,
        'Medium': 2,   'B': 2,
        'Low': 1,      'A': 1,
        'Unknown': 2
    }
    return mapping.get(value, 2)

def calculate_security_score(app_data):
    """
    Calculate Impact, Likelihood, and Total Score.
    Total Score = Impact Score * Likelihood Score
    """
    score_breakdown = {'impact_factors': {}, 'likelihood_factors': {}}
    
    # --- IMPACT FACTORS ---
    i_scores = {}
    i_scores['Data Classification'] = get_data_classification_score(app_data.get('dataClassification'))
    i_scores['Business Criticality'] = get_business_criticality_score(app_data.get('businessCriticality'))
    i_scores['Emergency Tier'] = get_emergency_tier_score(app_data.get('emergencyTier'))
    i_scores['Disaster Recovery RTO'] = get_disaster_recovery_rto_score(app_data.get('disasterRecoverRto'))
    i_scores['Disaster Recovery RPO'] = get_disaster_recovery_rpo_score(app_data.get('disasterRecoverRpo'))
    i_scores['User Base'] = get_userbase_score(app_data.get('userImpactExternal'), app_data.get('userImpactInternal'))
    
    has_ext_users = 'No'
    ext_val = app_data.get('userImpactExternal')
    if ext_val:
        try:
            if int(str(ext_val).replace(',', '')) > 0:
                has_ext_users = 'Yes'
        except: pass
    i_scores['External Users'] = get_external_users_score(has_ext_users)
    
    i_scores['External Facing'] = get_external_facing_score(app_data.get('externalFacing'))
    
    impact_score = sum(i_scores.values())
    
    # --- LIKELIHOOD FACTORS ---
    l_scores = {}
    l_scores['WAF Enabled'] = get_waf_enabled_score(app_data.get('wafEnabled'))
    l_scores['Application Ring Fenced'] = get_ring_fenced_score(app_data.get('applicationRingFenced'))
    l_scores['Existing EOL Systems'] = get_eol_score(app_data.get('existingEndOfLifeSystems'))
    l_scores['Other Security Issues'] = get_security_issues_score(app_data.get('numberOfExistingSecurityIssues'))
    l_scores['App Security Classification'] = get_app_security_classification_score(app_data.get('appSecurityRating'))
    
    likelihood_score = sum(l_scores.values())
    
    # --- TOTAL SCORE ---
    total_score = impact_score * likelihood_score
    
    # --- DETERMINING RATING ---
    if total_score >= 250:
        rating = 'Critical'
    elif 150 <= total_score < 250:
        rating = 'High'
    elif 75 < total_score < 150:
        rating = 'Medium'
    else:
        rating = 'Low'
    
    score_breakdown['impact_score'] = impact_score
    score_breakdown['likelihood_score'] = likelihood_score
    score_breakdown['impact_factors'] = i_scores
    score_breakdown['likelihood_factors'] = l_scores
    
    return total_score, rating, score_breakdown

def rate_applications(json_file_path):
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return []
    
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    
    applications = data.get('Applications', {})
    results = []
    
    for app_id, app_data in applications.items():
        if not isinstance(app_data, dict): continue
        score, rating, breakdown = calculate_security_score(app_data)
        results.append({
            'app_id': app_id,
            'app_name': app_data.get('businessApplicationName'),
            'portfolio': app_data.get('portfolio'),
            'total_score': score,
            'rating': rating,
            'score_breakdown': breakdown,
            'data_classification': app_data.get('dataClassification'),
            'criticality': app_data.get('businessCriticality'),
            'eol_systems': app_data.get('existingEndOfLifeSystems'),
            'waf_enabled': app_data.get('wafEnabled')
        })
    
    results.sort(key=lambda x: x['total_score'], reverse=True)
    return results

def print_report(results):
    total_apps = len(results)
    ratings_count = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    
    # Stats for Executives
    portfolios = {}
    eol_count = 0
    missing_waf_count = 0
    high_conf_data_count = 0
    
    for r in results:
        # Rating Counts
        if r['rating'] in ratings_count:
            ratings_count[r['rating']] += 1
            
        # Portfolio Stats
        p = r['portfolio'] if r['portfolio'] else "Unknown"
        if p not in portfolios:
            portfolios[p] = {'count': 0, 'total_score': 0, 'critical_apps': 0}
        portfolios[p]['count'] += 1
        portfolios[p]['total_score'] += r['total_score']
        if r['rating'] == 'Critical':
            portfolios[p]['critical_apps'] += 1
            
        # Hygiene Stats
        if r['eol_systems'] == 'Yes': eol_count += 1
        if r['waf_enabled'] == 'No': missing_waf_count += 1
        
        # Data Stats
        if r['data_classification'] == 'Red - Highly Confidential':
            high_conf_data_count += 1

    print("=" * 100)
    print("APPLICATION SECURITY ASSESSMENT REPORT")
    print("=" * 100)
    print()

    # --- SUMMARY SECTION ---
    print("SUMMARY:")
    print(f"Total Applications: {total_apps}")
    print("Rating Distribution:")
    for rating in ['Critical', 'High', 'Medium', 'Low']:
        count = ratings_count[rating]
        percentage = (count / total_apps * 100) if total_apps > 0 else 0
        print(f"  {rating}: {count} ({percentage:.1f}%)")
    print()

    # --- EXECUTIVE STATISTICS ---
    print("EXECUTIVE STATISTICS:")
    print("-" * 100)
    
    # 1. Portfolio Risk
    print("1. Portfolio Risk Profile (Avg Score / Critical Apps):")
    sorted_portfolios = sorted(portfolios.items(), key=lambda x: x[1]['total_score'] / x[1]['count'], reverse=True)
    for p_name, p_data in sorted_portfolios:
        avg = p_data['total_score'] / p_data['count']
        print(f"  - {p_name:<15}: Avg Score {int(avg):<3} | Critical Apps: {p_data['critical_apps']}")
    
    # 2. Key Risk Indicators
    print("\n2. Key Risk Indicators (Systemic Issues):")
    print(f"  - End-of-Life Systems:     {eol_count} apps ({eol_count/total_apps*100:.1f}%)")
    print(f"  - Missing WAF Protection:  {missing_waf_count} apps ({missing_waf_count/total_apps*100:.1f}%)")
    print(f"  - Highly Confidential Data:{high_conf_data_count} apps ({high_conf_data_count/total_apps*100:.1f}%)")
    
    # 3. Top 5 Riskiest
    print("\n3. Top 5 Highest Risk Applications:")
    for i, r in enumerate(results[:5]):
        print(f"  {i+1}. {r['app_name']} ({r['app_id']}) - Score: {r['total_score']} [{r['rating']}]")

    print()
    print("-" * 100)
    # -----------------------

    for category in ['Critical', 'High', 'Medium', 'Low']:
        subset = [r for r in results if r['rating'] == category]
        if not subset: continue
        
        print(f"\n{category.upper()} APPLICATIONS:")
        print("-" * 100)
        print(f"{'App ID':<15} {'Application Name':<35} {'Total':<8} {'Impact':<8} {'Likelihood':<10}")
        print("-" * 100)
        
        for r in subset:
            print(f"{r['app_id']:<15} {r['app_name'][:34]:<35} {r['total_score']:<8} {r['score_breakdown']['impact_score']:<8} {r['score_breakdown']['likelihood_score']:<10}")

if __name__ == "__main__":
    results = rate_applications('applications.json')
    if results:
        print_report(results)
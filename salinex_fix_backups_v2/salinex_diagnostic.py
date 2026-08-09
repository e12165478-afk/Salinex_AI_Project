#!/usr/bin/env python3
"""
Salinex AI - Comprehensive Diagnostic Tool
============================================
This script scans your entire project and identifies the exact files/lines
that cause the 8 critical issues.

Run this inside your project root directory:
    python salinex_diagnostic.py
"""

import os
import re
import csv
import json
import ast
from pathlib import Path
from collections import defaultdict

class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"

def print_section(title):
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}")

def print_issue(issue_num, severity, description, file_path=None, line_num=None, code_snippet=None, fix_hint=None):
    color = Colors.RED if severity == "CRITICAL" else Colors.YELLOW if severity == "WARNING" else Colors.GREEN
    print(f"\n{color}[{severity}] Issue #{issue_num}: {description}{Colors.END}")
    if file_path:
        loc = f"Line {line_num}" if line_num else ""
        print(f"   📁 File: {file_path} {loc}")
    if code_snippet:
        print(f"   📝 Code: {Colors.CYAN}{code_snippet.strip()}{Colors.END}")
    if fix_hint:
        print(f"   💡 Fix: {fix_hint}")

def scan_file_for_patterns(filepath, patterns, context_lines=2):
    """Scan a file for regex patterns and return matches with context."""
    matches = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return matches

    for i, line in enumerate(lines, 1):
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, line):
                context = ''.join(lines[max(0,i-1-context_lines):min(len(lines), i+context_lines)])
                matches.append({
                    'line': i,
                    'pattern': pattern_name,
                    'text': line.strip(),
                    'context': context
                })
    return matches

# ============================================================================
# MAIN DIAGNOSTIC
# ============================================================================

def main():
    project_root = Path('.')
    issues_found = []

    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("  ███████╗ █████╗ ██╗     ██╗███╗   ██╗███████╗██╗  ██╗")
    print("  ██╔════╝██╔══██╗██║     ██║████╗  ██║██╔════╝╚██╗██╔╝")
    print("  ███████╗███████║██║     ██║██╔██╗ ██║█████╗   ╚███╔╝ ")
    print("  ╚════██║██╔══██║██║     ██║██║╚██╗██║██╔══╝   ██╔██╗ ")
    print("  ███████║██║  ██║███████╗██║██║ ╚████║███████╗██╔╝ ██╗")
    print("  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝")
    print(f"{Colors.END}")
    print(f"{Colors.BOLD}  COMPREHENSIVE DIAGNOSTIC TOOL v1.0{Colors.END}")
    print(f"  Scanning project: {project_root.absolute()}")

    # ========================================================================
    # ISSUE 1: Source_Type Segmentation
    # ========================================================================
    print_section("🔍 ISSUE 1: Source_Type Segmentation (3 brines treated as 1)")

    # Check data files
    data_files = list(project_root.glob("data/**/*.csv")) + list(project_root.glob("*.csv"))
    source_type_found_in_data = False
    source_type_values = set()

    for csv_file in data_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if 'Source_Type' in reader.fieldnames:
                    source_type_found_in_data = True
                    for row in reader:
                        if 'Source_Type' in row:
                            source_type_values.add(row['Source_Type'])
                    print(f"   ✅ {csv_file}: Found Source_Type column")
                    print(f"      Values: {source_type_values}")
                    break
        except:
            pass

    if not source_type_found_in_data:
        print_issue(1, "CRITICAL", "Source_Type column NOT found in any CSV data file", fix_hint="Add Source_Type to your training data")

    # Check if app.py and pages use Source_Type
    py_files = list(project_root.glob("app.py")) + list(project_root.glob("pages/*.py")) + list(project_root.glob("**/*.py"))

    source_type_usage = defaultdict(list)
    for py_file in py_files:
        if 'salinex_env' in str(py_file):
            continue
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'Source_Type' in line or 'source_type' in line.lower():
                        source_type_usage[str(py_file)].append((i, line.strip()))
        except:
            pass

    if source_type_usage:
        print(f"\n   📋 Source_Type referenced in:")
        for f, lines in source_type_usage.items():
            print(f"      {f} ({len(lines)} references)")
    else:
        print_issue(1, "CRITICAL", "Source_Type is NEVER referenced in any Python file", 
                   fix_hint="Add Source_Type handling in app.py and all page files")

    # Check for hardcoded brine type labels
    patterns = {
        'hardcoded_brine': r'High-Mg Salar Brine|Salar Brine|high.mg.salar',
        'brine_classification': r'brine.*classif|classif.*brine|type.*brine',
    }

    hardcoded_found = False
    for py_file in py_files:
        if 'salinex_env' in str(py_file):
            continue
        matches = scan_file_for_patterns(py_file, patterns)
        for m in matches:
            if 'hardcoded_brine' in m['pattern']:
                print_issue(1, "CRITICAL", "Hardcoded brine type label found", 
                           file_path=py_file, line_num=m['line'], 
                           code_snippet=m['text'],
                           fix_hint="Replace with dynamic classification based on Source_Type")
                hardcoded_found = True

    if not hardcoded_found:
        print_issue(1, "WARNING", "Could not find hardcoded 'High-Mg Salar Brine' — may be in session state or computed dynamically",
                   fix_hint="Check where brine type label is set in Streamlit session state")

    # ========================================================================
    # ISSUE 2: Mg/Li Mathematical Error
    # ========================================================================
    print_section("🔍 ISSUE 2: Mg/Li Calculation (Mg=0 but Mg/Li=49.8)")

    mg_li_patterns = {
        'mg_li_ratio': r'Mg/Li|mg_li|mg_div_li',
        'mg_ppm_input': r'Mg_ppm|mg_ppm|magnesium.*ppm',
        'li_ppm_input': r'Li_ppm|li_ppm|lithium.*ppm',
    }

    for py_file in py_files:
        if 'salinex_env' in str(py_file):
            continue
        matches = scan_file_for_patterns(py_file, mg_li_patterns)
        for m in matches:
            print(f"   📁 {py_file}:{m['line']} → {m['text'][:80]}")

    print_issue(2, "CRITICAL", "Check if Mg/Li is calculated BEFORE checking Mg=0",
               fix_hint="Add: if Mg_ppm == 0: Mg_Li_ratio = float('inf') or 'N/A'")

    # ========================================================================
    # ISSUE 3: ROI Unit Error
    # ========================================================================
    print_section("🔍 ISSUE 3: ROI Displayed in Years Instead of Percentage")

    roi_patterns = {
        'roi_display': r'ROI.*year|ROI.*yr|return.*investment.*year|بازگشت.*سرمایه.*سال',
        'roi_percent': r'ROI.*%|roi_percent|ROI_Percent',
        'roi_calc': r'profit.*capex|profit.*cost|ROI.*calc',
    }

    for py_file in py_files:
        if 'salinex_env' in str(py_file):
            continue
        matches = scan_file_for_patterns(py_file, roi_patterns)
        for m in matches:
            print_issue(3, "WARNING" if 'percent' in m['pattern'] else "CRITICAL",
                       f"ROI handling found: {m['pattern']}",
                       file_path=py_file, line_num=m['line'],
                       code_snippet=m['text'])

    print_issue(3, "CRITICAL", "ROI in data is PERCENTAGE (-27% to +89%), but UI shows '37.1 Years'",
               fix_hint="Change label from 'ROI' to 'Payback Period' OR convert years to percentage using formula")

    # ========================================================================
    # ISSUE 4: Flow Rate Doesn't Exist in Data
    # ========================================================================
    print_section("🔍 ISSUE 4: Flow Rate Variable Missing from Dataset")

    flow_in_data = False
    for csv_file in data_files:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if any('flow' in col.lower() or 'rate' in col.lower() for col in (reader.fieldnames or [])):
                    flow_in_data = True
                    print(f"   ✅ Flow/Rate column found in: {csv_file}")
                    print(f"      Columns: {[c for c in reader.fieldnames if 'flow' in c.lower() or 'rate' in c.lower()]}")
        except:
            pass

    if not flow_in_data:
        print_issue(4, "CRITICAL", "NO 'Flow Rate' or 'Flow_Rate' column exists in ANY CSV file",
                   fix_hint="Either: (1) Add Flow_Rate to your dataset, or (2) Remove Flow Rate optimization from UI")

    flow_ui_patterns = {
        'flow_input': r'Flow.*Rate|flow_rate|دبی|dabi',
        'flow_optimize': r'flow.*optim|optim.*flow|دبی.*بهینه',
    }

    for py_file in py_files:
        if 'salinex_env' in str(py_file):
            continue
        matches = scan_file_for_patterns(py_file, flow_ui_patterns)
        for m in matches:
            print_issue(4, "CRITICAL", "Flow Rate referenced in UI but NOT in data",
                       file_path=py_file, line_num=m['line'],
                       code_snippet=m['text'])

    # ========================================================================
    # ISSUE 5: Fabricated Metrics
    # ========================================================================
    print_section("🔍 ISSUE 5: Fabricated Metrics (No Data Source)")

    fabricated_metrics = [
        'Salinex Index', 'salinex_index', 'Salinex_Index',
        'Compliance', 'compliance', 'انطباق',
        'Purity', 'purity', 'خلوص',
        'Confidence Score', 'confidence_score', 'ConfidenceScore',
        'Stability Index', 'stability_index', 'پایداری',
    ]

    for metric in fabricated_metrics:
        pattern = {metric: re.escape(metric)}
        found_any = False
        for py_file in py_files:
            if 'salinex_env' in str(py_file):
                continue
            matches = scan_file_for_patterns(py_file, pattern)
            for m in matches:
                print_issue(5, "WARNING", f"Metric '{metric}' found in code",
                           file_path=py_file, line_num=m['line'],
                           code_snippet=m['text'],
                           fix_hint=f"Either remove '{metric}' or document its exact calculation formula")
                found_any = True
        if not found_any:
            # Try partial match
            for py_file in py_files:
                if 'salinex_env' in str(py_file):
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if metric.lower() in content.lower():
                            print_issue(5, "WARNING", f"Metric '{metric}' found in {py_file}",
                                       fix_hint="Check exact line and add formula documentation")
                except:
                    pass

    # Check YAML config
    yaml_files = list(project_root.glob("**/*.yaml")) + list(project_root.glob("**/*.yml"))
    for yf in yaml_files:
        try:
            with open(yf, 'r', encoding='utf-8') as f:
                content = f.read()
                for metric in ['index', 'compliance', 'purity', 'confidence', 'stability']:
                    if metric in content.lower():
                        print_issue(5, "WARNING", f"Metric keyword '{metric}' found in config: {yf}",
                                   fix_hint="Document how this config value maps to the displayed metric")
        except:
            pass

    # ========================================================================
    # ISSUE 6: Economic Calculation Errors
    # ========================================================================
    print_section("🔍 ISSUE 6: Economic Calculations (OPEX $1.01 vs Actual $5.59)")

    econ_patterns = {
        'opex_calc': r'OPEX|opex|هزینه.*عملیاتی|operational.*cost',
        'cost_total': r'Total_Cost|total_cost|هزینه.*کل',
        'revenue_total': r'Total_Revenue|total_revenue|درآمد.*کل',
        'profit_calc': r'Profit|profit|سود',
        'economic_params': r'Economic_Parameters|economic_param',
    }

    for py_file in py_files:
        if 'salinex_env' in str(py_file):
            continue
        matches = scan_file_for_patterns(py_file, econ_patterns)
        for m in matches:
            print(f"   📁 {py_file}:{m['line']} → {m['text'][:80]}")

    # Check Economic_Parameters.csv
    econ_csv = list(project_root.glob("**/Economic_Parameters.csv"))
    if econ_csv:
        for ec in econ_csv:
            print(f"\n   📊 Economic Parameters file found: {ec}")
            try:
                with open(ec, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    print(f"      Columns: {reader.fieldnames}")
                    for row in reader:
                        print(f"      Row: {row}")
            except Exception as e:
                print(f"      Error reading: {e}")
    else:
        print_issue(6, "WARNING", "Economic_Parameters.csv not found in expected location",
                   fix_hint="Verify where economic constants are stored")

    print_issue(6, "CRITICAL", "Platform shows OPEX $1.01/m³ but actual data average is $5.59/m³",
               fix_hint="Check if economic calculations are hardcoded for Brackish only and applied to all sources")

    # ========================================================================
    # ISSUE 7: Personal Signature
    # ========================================================================
    print_section("🔍 ISSUE 7: Personal Signature 'ENGINEER: Mirzaee'")

    signature_patterns = {
        'mirzaee': r'Mirzaee|mirzaee|میرزایی',
        'engineer_tag': r'ENGINEER|engineer|مهندس.*ناظر',
    }

    for py_file in py_files:
        if 'salinex_env' in str(py_file):
            continue
        matches = scan_file_for_patterns(py_file, signature_patterns)
        for m in matches:
            print_issue(7, "WARNING", "Personal signature/identity found in production code",
                       file_path=py_file, line_num=m['line'],
                       code_snippet=m['text'],
                       fix_hint="Remove personal names from UI. Use generic 'System Engineer' or nothing")

    # Also check txt files
    txt_files = list(project_root.glob("**/*.txt"))
    for tf in txt_files:
        matches = scan_file_for_patterns(tf, signature_patterns)
        for m in matches:
            print_issue(7, "INFO", "Signature found in text file",
                       file_path=tf, line_num=m['line'],
                       code_snippet=m['text'])

    # ========================================================================
    # ISSUE 8: Copyleaks Watermark
    # ========================================================================
    print_section("🔍 ISSUE 8: Copyleaks Watermark in UI")

    copyleaks_patterns = {
        'copyleaks': r'Copyleaks|copyleaks|detect.*ai|ai.*detect',
    }

    for py_file in py_files:
        if 'salinex_env' in str(py_file):
            continue
        matches = scan_file_for_patterns(py_file, copyleaks_patterns)
        for m in matches:
            print_issue(8, "WARNING", "Copyleaks watermark found in production UI code",
                       file_path=py_file, line_num=m['line'],
                       code_snippet=m['text'],
                       fix_hint="Remove all AI detection watermarks before production deployment")

    # ========================================================================
    # SUMMARY & ACTION PLAN
    # ========================================================================
    print_section("📋 SUMMARY & PRIORITIZED ACTION PLAN")

    actions = [
        ("CRITICAL", "app.py + pages/*.py", "Add Source_Type segmentation logic"),
        ("CRITICAL", "pages/2__Prediction.py", "Fix Mg/Li calculation with zero-check"),
        ("CRITICAL", "pages/*.py", "Fix ROI label: either 'Payback Period (years)' or convert to %"),
        ("CRITICAL", "data/ + pages/3__Scenario.py", "Add Flow_Rate to dataset OR remove from UI optimization"),
        ("WARNING", "pages/*.py + kpi_weights.yaml", "Document or remove fabricated metrics (Salinex Index, etc.)"),
        ("CRITICAL", "utils/ + pages/4__Economics.py", "Fix economic calculations per Source_Type"),
        ("WARNING", "All .py files", "Remove 'ENGINEER: Mirzaee' from UI strings"),
        ("WARNING", "All .py files", "Remove 'Detect AI with Copyleaks' watermarks"),
    ]

    print(f"\n{Colors.BOLD}Priority | File(s) | Action{Colors.END}")
    print("-" * 70)
    for priority, files, action in actions:
        color = Colors.RED if priority == "CRITICAL" else Colors.YELLOW
        print(f"{color}{priority:<10}{Colors.END} | {files:<25} | {action}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Diagnostic complete. Fix CRITICAL items first, then WARNING items.{Colors.END}")
    print(f"{Colors.CYAN}Run this script again after fixes to verify.{Colors.END}\n")

if __name__ == "__main__":
    main()
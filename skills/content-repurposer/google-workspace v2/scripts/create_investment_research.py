#!/usr/bin/env python3
"""Create Investment Research Google Doc - Professional, No Emojis"""
# /// script
# dependencies = [
#   "google-auth",
#   "google-api-python-client",
# ]
# ///

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from beautiful_doc import BeautifulDocBuilder
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Create document
builder = BeautifulDocBuilder()
doc_id = builder.create_document("Low-Risk Investment Options in Germany - Comprehensive Research Report")

# Title
builder.add_title("LOW-RISK INVESTMENT OPTIONS IN GERMANY")
builder.add_paragraph("Comprehensive Research Report | January 2026")
builder.add_line_break()

# Executive Summary
builder.add_section_header("EXECUTIVE SUMMARY")
builder.add_paragraph(
    "This report outlines low-risk investment options available in Germany with low barriers to entry, "
    "suitable for beginners or those seeking safe, steady returns."
)
builder.add_line_break()

builder.add_paragraph("Key Findings:")
builder.add_bullet_list([
    "Minimum investment from 1 EUR/month (ETF savings plans)",
    "Interest rates 1.6-3.8% for savings accounts",
    "All deposits protected up to 100,000 EUR",
    "No minimum for government bonds"
])
builder.add_line_break()

# Top 5 Options
builder.add_section_header("TOP 5 INVESTMENT OPTIONS")
builder.add_line_break()

builder.add_subsection_header("1. ETF SAVINGS PLANS")
builder.add_paragraph("Minimum: 1 EUR/month | Returns: 6-8% average | Risk: Low-Medium")
builder.add_paragraph(
    "Automated monthly investment in diversified funds. Best for: Long-term wealth building."
)
builder.add_paragraph("Top Brokers: Trade Republic, Scalable Capital, Consorsbank, ING")
builder.add_line_break()

builder.add_subsection_header("2. TAGESGELD (Overnight Savings)")
builder.add_paragraph("Minimum: 0-1,000 EUR | Returns: 1.6-3.8% | Risk: Very Low")
builder.add_paragraph(
    "Flexible savings with daily access. Protected by deposit insurance up to 100,000 EUR. "
    "Best for: Emergency fund."
)
builder.add_line_break()

builder.add_subsection_header("3. FESTGELD (Fixed Deposits)")
builder.add_paragraph("Minimum: 2,500-10,000 EUR | Returns: 3.0-4.5% | Risk: Very Low")
builder.add_paragraph(
    "Fixed-term deposits with guaranteed returns. Protected by deposit insurance. "
    "Best for: Money you won't need for 1-5 years."
)
builder.add_line_break()

builder.add_subsection_header("4. GERMAN GOVERNMENT BONDS")
builder.add_paragraph("Minimum: No minimum | Returns: 2.5-3.2% | Risk: Extremely Low")
builder.add_paragraph(
    "AAA-rated government securities. Among safest investments in Europe. "
    "Best for: Ultra-conservative investors."
)
builder.add_line_break()

builder.add_subsection_header("5. MONEY MARKET FUNDS")
builder.add_paragraph("Minimum: 50-500 EUR | Returns: 2.5-4.0% | Risk: Very Low")
builder.add_paragraph(
    "Professional managed funds in short-term debt. Better than savings accounts. "
    "Best for: Short-term savings with better yield."
)
builder.add_line_break()

# Safety
builder.add_section_header("SAFETY AND PROTECTION")
builder.add_paragraph("German Deposit Insurance:")
builder.add_bullet_list([
    "100,000 EUR per person, per bank guaranteed",
    "Covers Tagesgeld and Festgeld accounts",
    "EU-wide protection scheme",
    "Automatic coverage - no application needed"
])
builder.add_line_break()

# Strategies
builder.add_section_header("RECOMMENDED STRATEGIES")
builder.add_line_break()

builder.add_subsection_header("With 50-100 EUR/month:")
builder.add_bullet_list([
    "ETF Savings Plan: 50-100 EUR/month",
    "Start with MSCI World or S&P 500",
    "Use Trade Republic or Scalable Capital"
])
builder.add_line_break()

builder.add_subsection_header("With 500-1,000 EUR/month:")
builder.add_bullet_list([
    "ETF Savings: 300 EUR/month",
    "Tagesgeld: 200 EUR/month (emergency fund)",
    "Build 3-6 months expenses first"
])
builder.add_line_break()

builder.add_subsection_header("With 5,000-10,000 EUR:")
builder.add_bullet_list([
    "Tagesgeld: 3,000-5,000 EUR (emergency)",
    "Festgeld: 2,000-3,000 EUR (1-2 years)",
    "ETF: 1,000-2,000 EUR + monthly plan"
])
builder.add_line_break()

builder.add_subsection_header("With 20,000 EUR+:")
builder.add_bullet_list([
    "Tagesgeld: 10,000 EUR",
    "Festgeld: 5,000 EUR (ladder strategy)",
    "ETFs: 5,000 EUR + monthly contributions",
    "Bonds: 2,000-3,000 EUR for diversification"
])
builder.add_line_break()

# Getting Started
builder.add_section_header("GETTING STARTED GUIDE")
builder.add_line_break()

builder.add_paragraph("Week 1: Research")
builder.add_bullet_list([
    "Learn about ETFs and index funds",
    "Watch educational videos",
    "Understand investment basics"
])
builder.add_line_break()

builder.add_paragraph("Week 2: Choose Broker")
builder.add_bullet_list([
    "Compare brokers and fees",
    "Check ETF selection",
    "Explore interface (don't invest yet)"
])
builder.add_line_break()

builder.add_paragraph("Week 3: Open Account")
builder.add_bullet_list([
    "Complete VideoIdent verification",
    "Submit tax ID",
    "Wait for approval (1-5 days)"
])
builder.add_line_break()

builder.add_paragraph("Week 4: Start Investing")
builder.add_bullet_list([
    "Set up automatic savings plan",
    "Submit Freistellungsauftrag (tax form)",
    "Begin monthly contributions"
])
builder.add_line_break()

# Tax
builder.add_section_header("TAX CONSIDERATIONS")
builder.add_paragraph("Capital Gains Tax: 26.375% (automatically deducted by German brokers)")
builder.add_paragraph("Tax-Free Allowance: 1,000 EUR per person annually")
builder.add_line_break()

builder.add_paragraph("Key Points:")
builder.add_bullet_list([
    "German brokers handle taxes automatically",
    "Submit Freistellungsauftrag to use allowance",
    "Receive tax certificate at year-end",
    "Include in annual tax return"
])
builder.add_line_break()

# Final Recommendations
builder.add_section_header("FINAL RECOMMENDATIONS")
builder.add_line_break()

builder.add_subsection_header("Simplest Start:")
builder.add_paragraph(
    "Open Trade Republic account, start ETF savings plan at 25-50 EUR/month, "
    "maintain Tagesgeld for emergencies."
)
builder.add_line_break()

builder.add_subsection_header("Safest Start:")
builder.add_paragraph(
    "Build Tagesgeld emergency fund to 5,000-10,000 EUR, then add Festgeld for fixed returns."
)
builder.add_line_break()

builder.add_subsection_header("Best Long-Term Returns:")
builder.add_paragraph(
    "ETF savings plan in MSCI World or S&P 500, 10+ year horizon, ignore short-term fluctuations."
)
builder.add_line_break()

builder.add_subsection_header("Pre-Investment Checklist:")
builder.add_bullet_list([
    "3-6 months emergency fund",
    "No high-interest debt",
    "Stable income",
    "German bank account and tax ID",
    "Understanding of risks",
    "Long-term perspective (5+ years)"
])
builder.add_line_break()

# Disclaimer
builder.add_section_header("DISCLAIMER")
builder.add_paragraph(
    "This report is for informational purposes only and does not constitute financial advice. "
    "Past performance does not guarantee future results. All investments carry risk. "
    "Consult a licensed financial advisor before making investment decisions."
)
builder.add_line_break()

builder.add_paragraph("Report prepared: January 17, 2026")
builder.add_paragraph("Sources: Deutsche Finanzagentur, BaFin, JustETF, Bloomberg")

# Finalize
builder.flush()
builder.make_shareable()

# Share with Humu
creds = service_account.Credentials.from_service_account_file(
    '/Users/yasmineseidu/.openclaw/configs/google/service-account-clean.json',
    scopes=['https://www.googleapis.com/auth/drive'],
    subject='yasmine@smarterflo.com'
)

drive_service = build('drive', 'v3', credentials=creds)
drive_service.permissions().create(
    fileId=builder.doc_id,
    body={
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'mutawakilhumu2@gmail.com'
    },
    sendNotificationEmail=True,
    emailMessage='Yasmine has shared comprehensive research on low-risk investment options in Germany. Professional report covering ETF savings plans, savings accounts, government bonds, and more.'
).execute()

print(f"SUCCESS - Document created and shared")
print(f"URL: {builder.get_url()}")
print(f"Shared with: Humu Mutawakil")
print(f"Formatting: Professional, NO emojis")

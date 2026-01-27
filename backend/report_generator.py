"""
PDF Report Generator for Valkyrie Security Tests
Generates comprehensive, professional security test reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.colors import HexColor
from datetime import datetime
from typing import Dict, List
import os


class SecurityReportGenerator:
    """Generate professional PDF security reports"""

    def __init__(self, test_data: Dict, findings: List[Dict], output_path: str):
        """
        Initialize report generator

        Args:
            test_data: Test metadata (name, target_url, status, dates, etc.)
            findings: List of vulnerability findings
            output_path: Path to save the PDF
        """
        self.test_data = test_data
        self.findings = findings
        self.output_path = output_path

        # Color scheme
        self.colors = {
            'primary': HexColor('#10b981'),  # Green
            'critical': HexColor('#ef4444'),  # Red
            'high': HexColor('#f97316'),      # Orange
            'medium': HexColor('#eab308'),    # Yellow
            'low': HexColor('#3b82f6'),       # Blue
            'header_bg': HexColor('#f9fafb'), # Light gray
            'text': HexColor('#1f2937'),      # Dark gray
        }

        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""

        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=self.colors['text'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.grey,
            spaceAfter=12,
            alignment=TA_CENTER,
        ))

        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderColor=self.colors['primary'],
            borderWidth=0,
            borderPadding=5,
        ))

        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=self.colors['text'],
            spaceAfter=8,
            spaceBefore=8,
            fontName='Helvetica-Bold',
        ))

        # Body text
        self.styles.add(ParagraphStyle(
            name='ReportBodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.colors['text'],
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ))

        # Code/monospace
        self.styles.add(ParagraphStyle(
            name='ReportCode',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Courier',
            textColor=HexColor('#1f2937'),
            backColor=HexColor('#f3f4f6'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=6,
        ))

    def generate_report(self):
        """Generate the complete PDF report"""

        # Create PDF document
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        # Build story (content)
        story = []

        # 1. Cover Page
        story.extend(self._build_cover_page())
        story.append(PageBreak())

        # 2. Executive Summary
        story.extend(self._build_executive_summary())
        story.append(PageBreak())

        # 3. Test Details
        story.extend(self._build_test_details())
        story.append(Spacer(1, 0.3*inch))

        # 4. Vulnerability Summary
        story.extend(self._build_vulnerability_summary())
        story.append(PageBreak())

        # 5. Detailed Findings
        story.extend(self._build_detailed_findings())

        # 6. Recommendations
        story.append(PageBreak())
        story.extend(self._build_recommendations())

        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)

        return self.output_path

    def _build_cover_page(self) -> List:
        """Build the cover page"""
        elements = []

        # Add spacing from top
        elements.append(Spacer(1, 1.2*inch))

        # Try to add logo if it exists (use black logo for PDF reports)
        logo_path = "frontend/public/black_logo.png"
        try:
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=1.5*inch, height=1.5*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.3*inch))
        except Exception as e:
            # If logo doesn't exist or can't be loaded, skip it
            pass

        # Title
        title = Paragraph("VALKYRIE", self.styles['CustomTitle'])
        elements.append(title)

        subtitle = Paragraph("Security Assessment Report", self.styles['CustomSubtitle'])
        elements.append(subtitle)

        elements.append(Spacer(1, 0.5*inch))

        # Horizontal line
        elements.append(Spacer(1, 0.2*inch))

        # Test name
        test_name = Paragraph(
            f"<b>{self.test_data.get('name', 'Security Test')}</b>",
            ParagraphStyle('TestName', parent=self.styles['Normal'], fontSize=18, alignment=TA_CENTER)
        )
        elements.append(test_name)

        elements.append(Spacer(1, 0.3*inch))

        # Target information
        target_info = [
            ['Target:', self.test_data.get('target_url', 'N/A')],
            ['Test Date:', self.test_data.get('created_at', 'N/A')],
            ['Status:', self.test_data.get('status', 'N/A').upper()],
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ]

        target_table = Table(target_info, colWidths=[1.5*inch, 4*inch])
        target_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), self.colors['text']),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.grey),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(target_table)
        elements.append(Spacer(1, 1*inch))

        # Confidentiality notice
        notice = Paragraph(
            "<b>CONFIDENTIAL</b><br/>"
            "This report contains sensitive security information and should be handled accordingly. "
            "Distribution should be limited to authorized personnel only.",
            ParagraphStyle('Notice', parent=self.styles['Normal'], fontSize=9,
                          alignment=TA_CENTER, textColor=colors.grey,
                          borderColor=colors.grey, borderWidth=1, borderPadding=10)
        )
        elements.append(notice)

        return elements

    def _build_executive_summary(self) -> List:
        """Build executive summary section"""
        elements = []

        # Section title
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.1*inch))

        # Count vulnerabilities by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for finding in self.findings:
            severity = finding.get('severity', 'low').lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

        total_vulns = sum(severity_counts.values())

        # Summary text
        summary_text = (
            f"This security assessment was conducted on <b>{self.test_data.get('target_url', 'the target application')}</b> "
            f"on {self.test_data.get('created_at', 'N/A')}. "
            f"The assessment identified <b>{total_vulns} security finding{'s' if total_vulns != 1 else ''}</b> "
            f"across various severity levels."
        )

        elements.append(Paragraph(summary_text, self.styles['ReportBodyText']))
        elements.append(Spacer(1, 0.2*inch))

        # Severity breakdown table
        severity_data = [
            ['Severity', 'Count', 'Risk Level'],
            ['Critical', str(severity_counts['critical']), 'Immediate action required'],
            ['High', str(severity_counts['high']), 'Urgent remediation needed'],
            ['Medium', str(severity_counts['medium']), 'Should be addressed'],
            ['Low', str(severity_counts['low']), 'Minor improvements'],
        ]

        severity_table = Table(severity_data, colWidths=[1.5*inch, 1*inch, 3.5*inch])
        severity_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['header_bg']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['text']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (0, 1), self.colors['critical']),
            ('TEXTCOLOR', (0, 2), (0, 2), self.colors['high']),
            ('TEXTCOLOR', (0, 3), (0, 3), self.colors['medium']),
            ('TEXTCOLOR', (0, 4), (0, 4), self.colors['low']),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))

        elements.append(severity_table)
        elements.append(Spacer(1, 0.2*inch))

        # Key findings
        if total_vulns > 0:
            elements.append(Paragraph("Key Findings:", self.styles['SubsectionHeading']))

            # Get top 3 critical/high findings
            critical_high = [f for f in self.findings if f.get('severity', '').lower() in ['critical', 'high']]
            top_findings = critical_high[:3] if critical_high else self.findings[:3]

            for i, finding in enumerate(top_findings, 1):
                finding_text = (
                    f"<b>{i}. {finding.get('title', 'Vulnerability')}</b> "
                    f"[{finding.get('severity', 'N/A').upper()}]<br/>"
                    f"{finding.get('description', 'No description available.')}"
                )
                elements.append(Paragraph(finding_text, self.styles['ReportBodyText']))
                elements.append(Spacer(1, 0.1*inch))

        return elements

    def _build_test_details(self) -> List:
        """Build test details section"""
        elements = []

        elements.append(Paragraph("Test Configuration", self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.1*inch))

        # Test details table
        test_details = [
            ['Test Name:', self.test_data.get('name', 'N/A')],
            ['Target URL:', self.test_data.get('target_url', 'N/A')],
            ['Authentication:', self.test_data.get('auth_type', 'none').upper()],
            ['Test Started:', self.test_data.get('created_at', 'N/A')],
            ['Test Completed:', self.test_data.get('completed_at', 'N/A')],
            ['Test Status:', self.test_data.get('status', 'N/A').upper()],
        ]

        details_table = Table(test_details, colWidths=[1.5*inch, 4.5*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), self.colors['text']),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(details_table)

        return elements

    def _build_vulnerability_summary(self) -> List:
        """Build vulnerability summary section"""
        elements = []

        elements.append(Paragraph("Vulnerability Summary", self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.1*inch))

        if not self.findings:
            elements.append(Paragraph(
                "No vulnerabilities were identified during this security assessment.",
                self.styles['ReportBodyText']
            ))
            return elements

        # Group findings by vulnerability type
        vuln_types = {}
        for finding in self.findings:
            vtype = finding.get('vulnerability_type', 'unknown')
            if vtype not in vuln_types:
                vuln_types[vtype] = []
            vuln_types[vtype].append(finding)

        # Create summary table
        summary_data = [['Vulnerability Type', 'Count', 'Highest Severity']]

        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}

        for vtype, findings in sorted(vuln_types.items()):
            count = len(findings)
            highest_severity = max(findings, key=lambda f: severity_order.get(f.get('severity', 'low').lower(), 0))
            summary_data.append([
                vtype.replace('_', ' ').title(),
                str(count),
                highest_severity.get('severity', 'N/A').upper()
            ])

        summary_table = Table(summary_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['header_bg']),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.colors['text']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))

        elements.append(summary_table)

        return elements

    def _build_detailed_findings(self) -> List:
        """Build detailed findings section"""
        elements = []

        elements.append(Paragraph("Detailed Findings", self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.2*inch))

        if not self.findings:
            elements.append(Paragraph(
                "No vulnerabilities were identified during this assessment.",
                self.styles['ReportBodyText']
            ))
            return elements

        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_findings = sorted(
            self.findings,
            key=lambda f: severity_order.get(f.get('severity', 'low').lower(), 4)
        )

        # Add each finding
        for i, finding in enumerate(sorted_findings, 1):
            finding_elements = self._build_single_finding(i, finding)
            elements.extend(finding_elements)

            # Add spacing between findings
            if i < len(sorted_findings):
                elements.append(Spacer(1, 0.2*inch))

        return elements

    def _build_single_finding(self, number: int, finding: Dict) -> List:
        """Build a single detailed finding"""
        elements = []

        severity = finding.get('severity', 'low').lower()
        severity_color = self.colors.get(severity, colors.grey)

        # Finding header with number and title
        header_text = f"<b>Finding {number}: {finding.get('title', 'Vulnerability')}</b>"
        elements.append(Paragraph(header_text, self.styles['SubsectionHeading']))

        # Severity badge
        severity_badge = Paragraph(
            f"<b>SEVERITY: {severity.upper()}</b>",
            ParagraphStyle('SeverityBadge', parent=self.styles['Normal'],
                          fontSize=10, textColor=colors.white,
                          backColor=severity_color, alignment=TA_CENTER,
                          leftIndent=0, rightIndent=0, spaceBefore=0, spaceAfter=6)
        )
        elements.append(severity_badge)

        # Details table
        details = [
            ['Endpoint:', finding.get('endpoint', 'N/A')],
            ['Method:', finding.get('method', 'N/A')],
            ['Vulnerability Type:', finding.get('vulnerability_type', 'N/A').replace('_', ' ').title()],
        ]

        if finding.get('cvss_score'):
            details.append(['CVSS Score:', str(finding.get('cvss_score'))])

        details_table = Table(details, colWidths=[1.5*inch, 4.5*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text']),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 0.1*inch))

        # Description
        if finding.get('description'):
            elements.append(Paragraph("<b>Description:</b>", self.styles['ReportBodyText']))
            elements.append(Paragraph(finding.get('description'), self.styles['ReportBodyText']))
            elements.append(Spacer(1, 0.1*inch))

        # Proof of Concept
        if finding.get('proof_of_concept'):
            elements.append(Paragraph("<b>Proof of Concept:</b>", self.styles['ReportBodyText']))
            poc_text = finding.get('proof_of_concept', '').replace('<', '&lt;').replace('>', '&gt;')
            elements.append(Paragraph(poc_text, self.styles['ReportCode']))
            elements.append(Spacer(1, 0.1*inch))

        # Remediation
        if finding.get('remediation'):
            elements.append(Paragraph("<b>Remediation:</b>", self.styles['ReportBodyText']))
            elements.append(Paragraph(finding.get('remediation'), self.styles['ReportBodyText']))

        # Separator line
        elements.append(Spacer(1, 0.1*inch))

        return elements

    def _build_recommendations(self) -> List:
        """Build recommendations section"""
        elements = []

        elements.append(Paragraph("Recommendations", self.styles['SectionHeading']))
        elements.append(Spacer(1, 0.1*inch))

        recommendations = [
            {
                'title': 'Immediate Actions',
                'items': [
                    'Address all Critical and High severity vulnerabilities immediately',
                    'Implement security fixes in a test environment before production deployment',
                    'Conduct re-testing after remediation to verify fixes'
                ]
            },
            {
                'title': 'Short-term Improvements',
                'items': [
                    'Resolve Medium severity vulnerabilities within 30 days',
                    'Implement security monitoring and logging for detected attack patterns',
                    'Review and update security policies and procedures'
                ]
            },
            {
                'title': 'Long-term Strategy',
                'items': [
                    'Address Low severity findings during regular maintenance cycles',
                    'Implement security training for development team',
                    'Establish regular security assessment schedule (quarterly recommended)',
                    'Integrate security testing into CI/CD pipeline',
                    'Consider implementing a Web Application Firewall (WAF)'
                ]
            }
        ]

        for rec in recommendations:
            elements.append(Paragraph(rec['title'] + ':', self.styles['SubsectionHeading']))

            for item in rec['items']:
                bullet = Paragraph(f"• {item}", self.styles['ReportBodyText'])
                elements.append(bullet)

            elements.append(Spacer(1, 0.15*inch))

        # Closing statement
        closing = Paragraph(
            "<b>Note:</b> This report reflects the security posture at the time of testing. "
            "Security is an ongoing process, and regular assessments are recommended to maintain "
            "a strong security posture.",
            ParagraphStyle('Closing', parent=self.styles['ReportBodyText'],
                          borderColor=self.colors['primary'], borderWidth=1,
                          borderPadding=10, backColor=HexColor('#f0fdf4'))
        )
        elements.append(closing)

        return elements

    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()

        # Footer
        footer_text = f"Valkyrie Security Report | {self.test_data.get('name', 'Security Assessment')} | Page {doc.page}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(4.25*inch, 0.5*inch, footer_text)

        # Header line on non-first pages
        if doc.page > 1:
            canvas.setStrokeColor(self.colors['primary'])
            canvas.setLineWidth(2)
            canvas.line(0.75*inch, 10.5*inch, 7.75*inch, 10.5*inch)

        canvas.restoreState()


def generate_security_report(test_data: Dict, findings: List[Dict], output_path: str) -> str:
    """
    Generate a security assessment PDF report

    Args:
        test_data: Test metadata dictionary
        findings: List of vulnerability findings
        output_path: Path where PDF should be saved

    Returns:
        Path to the generated PDF file
    """
    generator = SecurityReportGenerator(test_data, findings, output_path)
    return generator.generate_report()

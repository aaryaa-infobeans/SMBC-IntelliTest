#!/usr/bin/env python3
"""
Pytest Results PDF Report Generator
Generates a comprehensive PDF report from pytest-json-report results.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PytestReportGenerator:
    """Generate PDF reports from pytest-json-report results."""

    def __init__(self, results_file: str, output_file: Optional[str] = None, detailed: bool = False):
        self.results_file = Path(results_file)
        self.output_file = Path(output_file) if output_file else self.results_file.parent / "SMBC-IntelliTest_test_summary.pdf"
        self.data: Optional[Dict[str, Any]] = None
        self.styles = getSampleStyleSheet()
        self.detailed = detailed
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles for the report."""
        self.styles.add(
            ParagraphStyle(
                name="CustomTitle",
                parent=self.styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.darkblue,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=colors.darkblue,
            )
        )

    def load_results(self):
        """Load and parse the pytest results JSON file."""
        try:
            with open(self.results_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            print(f"✓ Loaded pytest results from {self.results_file}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Results file not found: {self.results_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in results file: {e}")

    def _extract_test_data(self) -> List[Dict[str, Any]]:
        """Extract test case data from pytest results."""
        test_cases: List[Dict[str, Any]] = []

        if self.data is None:
            return test_cases

        # pytest-json-report structure
        for test in self.data.get("tests", []):
            test_file = test.get("nodeid", "").split("::")[0]
            test_name = test.get("nodeid", "").split("::")[-1]

            duration_sec = round(test.get("duration", 0), 2)
            outcome = test.get("outcome", "unknown")

            # Map pytest outcomes to our status
            status_mapping = {"passed": "passed", "failed": "failed", "skipped": "skipped", "error": "failed"}
            status = status_mapping.get(outcome, "unknown")

            # Get error message if failed
            error_msg = ""
            if outcome in ["failed", "error"] and test.get("call", {}).get("longrepr"):
                error_msg = str(test["call"]["longrepr"])[:100]

            test_cases.append(
                {
                    "spec_file": test_file,
                    "suite_title": test_file.replace(".py", "").replace("/", "."),
                    "test_title": test_name,
                    "status": status,
                    "duration_sec": duration_sec,
                    "start_time": "",  # pytest-json-report doesn't include start time
                    "error_message": error_msg,
                    "worker_index": "N/A",
                }
            )

        return test_cases

    def _get_summary_stats(self) -> Dict[str, Any]:
        """Calculate summary statistics from pytest results."""
        if self.data is None:
            return {}

        summary = self.data.get("summary", {})

        total_tests = summary.get("total", 0)
        passed_tests = summary.get("passed", 0)
        failed_tests = summary.get("failed", 0)
        skipped_tests = summary.get("skipped", 0)
        error_tests = summary.get("error", 0)

        # Combine failed and error
        failed_tests += error_tests

        duration_sec = self.data.get("duration", 0)
        duration_min = round(duration_sec / 60, 2)

        # Get start time from created timestamp
        created = self.data.get("created", "")
        formatted_start_time = ""
        # if created:
        #     try:
        #         dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
        #         formatted_start_time = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        #     except:
        #         formatted_start_time = created
        from datetime import datetime, timezone

        if created:
            try:
                # Convert to float first (because it's "seconds.sss")
                ts = float(created)
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)  # Always in UTC
                formatted_start_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
            except Exception as e:
                print(f"Failed to parse created timestamp: {e}")
                formatted_start_time = created

        pass_rate = round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0

        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "flaky_tests": 0,  # pytest doesn't track flaky by default
            "duration_minutes": duration_min,
            "start_time": formatted_start_time,
            "pass_rate": pass_rate,
            "config_file": "pytest.ini",
            "pytest_version": self.data.get("pytest_version", "N/A"),
            "workers": 1,  # Default for pytest
        }

    def _wrap_text(self, text: str, max_length: int) -> str:
        """Wrap text to fit in table cells with line breaks."""
        if not text or len(text) <= max_length:
            return text

        words = text.split(" ")
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(" ".join(current_line))

        return "\n".join(lines)

    def _create_summary_table(self, stats: Dict[str, Any]) -> Table:
        """Create the summary statistics table."""
        data = [
            ["Metric", "Value"],
            ["Total Test Cases", str(stats["total_tests"])],
            ["Passed", f"{stats['passed_tests']} ({stats['pass_rate']}%)"],
            ["Failed", str(stats["failed_tests"])],
            ["Skipped", str(stats["skipped_tests"])],
            ["Execution Duration", f"{stats['duration_minutes']} minutes"],
            ["Start Time", stats["start_time"]],
            ["Pytest Version", stats["pytest_version"]],
        ]

        table = Table(data, colWidths=[2 * inch, 2 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        return table

    def _create_test_results_table(self, test_cases: List[Dict[str, Any]]) -> Table:
        """Create the detailed test results table."""
        # Header
        data = [["Test File", "Test Case", "Status", "Duration (s)"]]

        # Add test case data
        for test in test_cases:
            status_text = test["status"].upper()
            wrapped_test_name = self._wrap_text(test["test_title"], 60)

            data.append(
                [
                    Paragraph(test["spec_file"], self.styles["Normal"]),
                    Paragraph(wrapped_test_name, self.styles["Normal"]),
                    Paragraph(status_text, self.styles["Normal"]),
                    Paragraph(str(test["duration_sec"]), self.styles["Normal"]),
                ]
            )

        # Adjust column widths for landscape orientation
        table = Table(data, colWidths=[2.0 * inch, 5.5 * inch, 1.0 * inch, 1.0 * inch])

        # Apply table style
        style_commands = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("TOPPADDING", (0, 0), (-1, 0), 10),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]

        # Add status-specific coloring
        for i, test in enumerate(test_cases, 1):
            if test["status"] == "passed":
                style_commands.append(("BACKGROUND", (2, i), (2, i), colors.lightgreen))
            elif test["status"] == "failed":
                style_commands.append(("BACKGROUND", (2, i), (2, i), colors.lightcoral))
            elif test["status"] == "skipped":
                style_commands.append(("BACKGROUND", (2, i), (2, i), colors.lightyellow))

        table.setStyle(TableStyle(style_commands))
        return table

    def _create_pie_chart(self, stats: Dict[str, Any]) -> Drawing:
        """Create a pie chart showing test results distribution with a modern look."""
        # Create a larger drawing for better visualization
        drawing = Drawing(400, 300)

        # Data for pie chart
        data = []
        labels = []
        colors_list = []

        # Define colors with better contrast
        colors_map = {
            "passed": colors.HexColor("#4CAF50"),  # Green
            "failed": colors.HexColor("#F44336"),  # Red
            "skipped": colors.HexColor("#FFC107"),  # Amber
            "other": colors.HexColor("#9E9E9E"),  # Grey
        }

        # Add data points for each status
        statuses = [
            ("passed_tests", "Passed", colors_map["passed"]),
            ("failed_tests", "Failed", colors_map["failed"]),
            ("skipped_tests", "Skipped", colors_map["skipped"]),
        ]

        for status, label, color in statuses:
            count = stats.get(status, 0)
            if count > 0:
                data.append(count)
                labels.append(f"{label} ({count})")
                colors_list.append(color)

        # Only create pie chart if we have data
        if not data:
            return drawing

        # Create pie chart with better styling
        pie = Pie()
        pie.x = 100  # Centered in the drawing
        pie.y = 50
        pie.width = 200
        pie.height = 200
        pie.data = data
        pie.labels = labels

        # Styling
        pie.slices.strokeWidth = 1
        pie.slices.strokeColor = colors.white
        pie.slices.fontName = "Helvetica-Bold"
        pie.slices.fontSize = 10
        pie.slices.labelRadius = 0.85  # Move labels closer to center
        pie.sideLabels = 1  # This prevents label overlap

        # Set colors and add effects
        for i, color in enumerate(colors_list):
            pie.slices[i].fillColor = color
            pie.slices[i].popout = 3 if i == 0 else 0  # Slightly pop the first slice
            pie.slices[i].strokeWidth = 0.5

        # Add a legend box
        from reportlab.graphics.charts.legends import Legend

        legend = Legend()
        legend.alignment = "right"
        legend.x = 50
        legend.y = 20
        legend.dx = 8
        legend.dy = 8
        legend.columnMaximum = 1  # only 1 item per column → grows horizontally
        legend.deltax = 60  # horizontal gap between legend columns
        legend.deltay = 0  # no extra vertical gap
        legend.variColumn = 1
        # legend.subCols = 3
        legend.colorNamePairs = [(color, label) for color, label in zip(colors_list, labels)]

        drawing.add(pie)
        drawing.add(legend)

        return drawing

    def _create_spec_file_summary(self, test_cases: List[Dict[str, Any]]) -> Table:
        """Create summary table by spec file."""
        spec_summary = {}

        for test in test_cases:
            spec_file = test["spec_file"]
            if spec_file not in spec_summary:
                spec_summary[spec_file] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "total_duration": 0}

            spec_summary[spec_file]["total"] += 1
            spec_summary[spec_file]["total_duration"] += test["duration_sec"]

            if test["status"] == "passed":
                spec_summary[spec_file]["passed"] += 1
            elif test["status"] == "failed":
                spec_summary[spec_file]["failed"] += 1
            elif test["status"] == "skipped":
                spec_summary[spec_file]["skipped"] += 1

        # Create table data
        data = [
            [
                "Test File\n",
                "Total tests\n",
                "Passed\n",
                "Failed\n",
                "Skipped\n",
                "Total\nDuration (s)",
                "Pass\nRate (%)",
            ]
        ]

        for spec_file, summary in spec_summary.items():
            pass_rate = round((summary["passed"] / summary["total"] * 100), 1) if summary["total"] > 0 else 0
            total_duration = round(summary["total_duration"], 2)

            styles = getSampleStyleSheet()
            styleN = styles["Normal"]

            data.append(
                [
                    Paragraph(spec_file, styleN),
                    str(summary["total"]),
                    str(summary["passed"]),
                    str(summary["failed"]),
                    str(summary["skipped"]),
                    str(total_duration),
                    f"{pass_rate}%",
                ]
            )

        table = Table(
            data, colWidths=[2 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch, 0.8 * inch]
        )
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTSIZE", (0, 1), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                ]
            )
        )

        return table

    def generate_report(self):
        """Generate the complete PDF report."""
        if not self.data:
            self.load_results()

        test_cases = self._extract_test_data()
        stats = self._get_summary_stats()

        # Create PDF document
        doc = SimpleDocTemplate(
            str(self.output_file),
            pagesize=landscape(A4),
            title="Pytest Execution Report",
            author="Automated Test Framework",
            leftMargin=0.5 * inch,
            rightMargin=0.5 * inch,
            topMargin=0.3 * inch,
            bottomMargin=0.5 * inch,
        )

        # Build the document
        elements = []

        # Title Page with Summary
        centered_title = ParagraphStyle("CenteredTitle", parent=self.styles["CustomTitle"], alignment=TA_CENTER)
        elements.append(Paragraph("Test Execution Report", centered_title))
        # elements.append(Spacer(1, 0.3 * inch))

        # Add report metadata
        meta_table = Table(
            [
                ["Execution Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ["Total tests:", str(stats["total_tests"])],
                ["Pass Rate:", f"{stats['pass_rate']}%"],
                ["Duration:", f"{stats['duration_minutes']:.2f} minutes"],
            ],
            colWidths=[1.5 * inch, 3 * inch],
        )

        meta_table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    # ('TOPPADDING', (0, 0), (-1, -1), 2),
                    # ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                    ("ALIGN", (1, 0), (1, -1), "LEFT"),
                    ("FONTWEIGHT", (0, 0), (0, -1), "BOLD"),
                ]
            )
        )

        elements.append(meta_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Create a side-by-side layout with pie chart and summary statistics
        side_by_side = Table(
            [
                # First row: Section headers
                ["Test Results Distribution", "Summary Statistics"],
                # Second row: Content
                [
                    # Left cell: Pie Chart
                    self._create_pie_chart(stats),
                    # Right cell: Summary Table
                    self._create_summary_table(stats),
                ],
            ],
            colWidths=[doc.width / 2.0] * 2,
            rowHeights=[0.4 * inch, 4 * inch],
        )

        # Style the side-by-side table
        side_by_side.setStyle(
            TableStyle(
                [
                    # Header row
                    ("ALIGN", (0, 0), (1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (1, 0), "MIDDLE"),
                    ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (1, 0), 12),
                    ("BOTTOMPADDING", (0, 0), (1, 0), 10),
                    # Content row
                    ("VALIGN", (0, 1), (1, 1), "MIDDLE"),
                    ("ALIGN", (0, 1), (0, 1), "CENTER"),
                    ("ALIGN", (1, 1), (1, 1), "CENTER"),
                    ("PADDING", (0, 1), (1, 1), 10),
                    # Grid and borders
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.black),
                ]
            )
        )

        elements.append(side_by_side)

        # Only add detailed sections if detailed flag is True
        if self.detailed:
            elements.append(PageBreak())
            centered_title = ParagraphStyle(
                "CenteredTitle",
                parent=self.styles["SectionHeader"],
                alignment=TA_CENTER,
            )

            # Test File Summary
            elements.append(Paragraph("Test File Summary", centered_title))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(self._create_spec_file_summary(test_cases))

            elements.append(PageBreak())

            # Detailed Test Results
            elements.append(Paragraph("Detailed Test Results", centered_title))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(self._create_test_results_table(test_cases))

        # Build the PDF document
        # Ensure landscape orientation is applied on every page. While pagesize=landscape(A4)
        # should be sufficient, some page templates/viewers may render portrait unless
        # the canvas page size is explicitly enforced per page.
        def _force_landscape(canvas, document):
            canvas.setPageSize(landscape(A4))

        doc.build(elements, onFirstPage=_force_landscape, onLaterPages=_force_landscape)

        return str(self.output_file)


def main():
    """Main function to generate the report."""
    import argparse

    # check if report.json or results.json exists, and assign to default
    if os.path.exists(".report.json"):
        default_file = ".report.json"
    elif os.path.exists("test-results.json"):
        default_file = "test-results.json"
    else:
        print(".report.json or results.json not found")
        return 1
    parser = argparse.ArgumentParser(description="Generate PDF report from pytest results")
    parser.add_argument(
        "results_file",
        nargs="?",
        default=default_file,
        help="Path to the pytest results JSON file (default: .report.json)",
    )
    parser.add_argument("-o", "--output", help="Output PDF file path")
    parser.add_argument("--detailed", action="store_true", help="Generate detailed report with test case information")

    args = parser.parse_args()

    try:
        generator = PytestReportGenerator(
            results_file=args.results_file, output_file=args.output, detailed=args.detailed
        )
        output_file = generator.generate_report()

        print("\n🎉 Report generation completed successfully!")
        print(f"📄 Output file: {output_file}")
        print(f"🔍 Report type: {'Detailed' if args.detailed else 'Summary'}")

        # Print summary
        stats = generator._get_summary_stats()
        print("\n📊 Test Execution Summary:")
        print(f"   Total tests: {stats['total_tests']}")
        print(f"   Passed: {stats['passed_tests']} ({stats['pass_rate']}%)")
        print(f"   Failed: {stats['failed_tests']}")
        print(f"   Skipped: {stats['skipped_tests']}")
        print(f"   Duration: {stats['duration_minutes']:.2f} minutes")

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

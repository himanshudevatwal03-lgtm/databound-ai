# Sample Data

Sample files for manually testing upload/extraction and, from Phase 5
onward, the anti-hallucination behavior described in the main README:

- `student_data.txt` / `company_data.txt` — plain text
- `employees.csv` — structured CSV (name, department, salary, years_experience)
- `project_requirements.pdf` — a 3-page generated PDF (deadline, scope,
  and testing-responsibility facts spread across pages, useful for
  testing page-numbered citations later)

`generate_sample_pdf.py` is the one-off script that produced the PDF —
see the comment at the top of that file if you ever need to regenerate it
with different content.

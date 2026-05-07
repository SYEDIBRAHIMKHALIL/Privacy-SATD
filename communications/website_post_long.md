# Privacy-SATD Miner: A First Pass at Privacy Self-Admitted Technical Debt

We built a pipeline to scan public OSS repositories for privacy-related self-admitted technical debt. The goal is to surface early signals and construct a dataset that supports later validation. We do not treat these outputs as compliance judgments.

The pipeline collects pull requests, issues, commits, and commit comments. It normalizes text, applies a privacy keyword filter, and maps candidates to GDPR articles using keyword overlap. We then generate a report, charts, and a static dashboard for review.

First run highlights:
- 186 filtered instances across 35 repos
- Top keywords: tracking, encryption, consent
- GDPR mapping skewed toward Art.32, then Art.6 and Art.7

We plan to add manual labeling with two annotators, measure precision and recall, and study false positive burden with practitioners.

If you are working on privacy tooling, I would value feedback on keyword coverage and false positives.

References:
- Diaz Ferreyra, Shahin, Zahedi, Quadri, Scandariato. MSR 2024. DOI 10.1145/3643991.3644909
- Diaz Ferreyra, Khelifi, Arachchilage, Scandariato. arXiv:2412.16667

Links:
Website: [WEBSITE URL]
GitHub: https://github.com/SYEDIBRAHIMKHALIL/Privacy-SATD

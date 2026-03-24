# Courses Repo

Shared course materials for CS 417, IT 612, and CS 675. Students fork this repo and work in Codespaces.

**Owner**: Matt

## Repo Structure

```
<course>/
  labs/<topic>/              # labs/binary-search/
  exercises/<topic>/         # exercises/log-analyzer/
  assignments/<topic>/       # assignments/basic-bash/
  assessments/<topic>/       # assessments/midterm-review/
```

## Naming Conventions

- **All directories are kebab-case.** No PascalCase, no snake_case, no numbers in directory names.
- **Name by topic, not by sequence number.** `labs/binary-search/` not `labs/lab-10/`. Numbering lives on Canvas, not in the repo. This keeps materials portable across weeks, semesters, and courses.
- **Existing directories** that don't follow this convention stay as-is (mid-semester). New work follows the convention.

## Content Types

| Type | Repo path | What it is |
|---|---|---|
| **Lab** | `<course>/labs/<topic>/` | Graded, test-gated, submitted via GitHub URL |
| **Exercise** | `<course>/exercises/<topic>/` | Guided walkthrough, submitted via GitHub URL |
| **Assignment** | `<course>/assignments/<topic>/` | Graded homework, submitted via GitHub URL |
| **Assessment** | `<course>/assessments/<topic>/` | Quizzes, exams, review materials |

## Canvas Posting Conventions

When posting to Canvas, use these assignment group mappings:

| Content | Canvas Assignment Group | Module Item Type |
|---|---|---|
| Lab | Assignments | Assignment |
| Exercise | Assignments | Assignment |
| Assignment | Assignments | Assignment |
| Quiz | Quizzes | Assignment |
| Discussion post | Participation | Assignment (graded discussion) |
| Slides / lecture | — (not graded) | ExternalUrl |

All assignments create as **draft** — Matt publishes after review.

## Submission Model

Students fork this repo, work in their fork (via Codespaces), and submit the URL to their GitHub repo on Canvas. Each assignment directory includes a README with setup instructions and (where applicable) a test runner.

Fork sync instructions are included in each README for students who already forked from a previous assignment.

# MatLex Desktop v11.5.0 validation

Validated before packaging:

- 610 concept records pass the concrete-example quality checks.
- 999 professional-English vocabulary records remain present in the TTS manifest.
- All 7 inline JavaScript blocks pass `node --check`.
- `package.json` parses successfully and reports version 11.5.0.
- GitHub Actions workflow parses as valid YAML and uploads `MatLex-Desktop-Windows-v11.5.0`.
- Desktop dashboard layout was rendered at 1536x960, 1200x800, and 1000x720 using the same final CSS.
- Interview and concept share the same module selectors and layout system.
- At 1536px the dashboard content uses a 1320px workspace, the overview is a normal grid member, and there is no horizontal overflow.
- At 1200px and 1000px the dashboard becomes a single-column layout and remains within the viewport.
- Library mode removes the dashboard overview/aside, uses the full workspace, and renders 3 columns on wide screens / 2 columns on narrower desktop screens.
- Module page scrolling belongs to the outer module screen, so the scrollbar is at the far-right edge of the window rather than inside a middle content column.

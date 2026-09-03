# Desktop UI Contract

The Tkinter desktop workflow exposes the feature without making the GUI responsible for route
calculation or persistence rules.

## Required Views and Actions

- Journey point list with add, modify, and delete actions.
- Origin and optional destination selection.
- Cost criterion and weighted-metric inputs.
- Optimize action with progress or busy state.
- Result summary showing ordered points, criterion, cost, metrics, exactness, and errors.
- Map view showing point markers and route geometry when available.
- Saved journey and result loading behavior.

## Behavioral Rules

- Invalid forms are rejected before optimization.
- Optimization runs outside the Tkinter event-handling path.
- Success and categorized failures return the UI to an actionable state.
- The UI never presents an approximate or unverified route as exact optimal output.
- When geometry is unavailable, the result remains inspectable and the map communicates that state.

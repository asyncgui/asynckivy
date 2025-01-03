# UI components with the following principles in mind.

- Fully take the advantages of the async/await syntax (of course).
- Do not use `touch.grab()` as it has a problem.
- Do not simulate touch events as it causes a lot of problems.
  - This allows a button to respond to touch events immediately, even when a `ScrollView` is in its parent stack.

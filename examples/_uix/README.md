# UI components with the following principles in mind.

- Fully utilize the advantages of the `async/await` syntax.
- Avoid using `touch.grab()`, as it has a problem.
  - Instead, receive touch events directly from `kivy.core.window.Window`.
- Refrain from simulating touch events, as it causes a lot of problems.
  - This allows widgets to respond to touch events immediately, even when a widget like `ScrollView` is in their parent stack.
    - Actually, not the official `ScrollView` but my own one, which is going to be added here.

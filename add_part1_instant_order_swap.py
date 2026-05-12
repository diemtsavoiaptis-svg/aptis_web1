from pathlib import Path

tpl_path = Path("templates/core/admin_part1_questions.html")
html = tpl_path.read_text(encoding="utf-8-sig")

old_input = '''<input class="num-input" type="number" name="question_number_{{ q.id }}" value="{{ q.question_number }}">'''

new_input = '''<input class="num-input part1-order-input" type="number" name="question_number_{{ q.id }}" value="{{ q.question_number }}" data-original-value="{{ q.question_number }}">'''

if old_input in html:
    html = html.replace(old_input, new_input)
elif "part1-order-input" not in html:
    raise SystemExit("Could not find Part 1 STT input to patch.")

swap_js = r'''
<script id="part1-instant-order-swap">
(function () {
    function normalizeNumber(value) {
        const n = parseInt(String(value || "").trim(), 10);
        return Number.isFinite(n) ? n : null;
    }

    function setupInstantOrderSwap() {
        const inputs = Array.from(document.querySelectorAll(".part1-order-input"));

        inputs.forEach(input => {
            if (input.dataset.swapReady === "1") return;
            input.dataset.swapReady = "1";

            input.addEventListener("focus", function () {
                this.dataset.beforeEditValue = this.value;
            });

            input.addEventListener("change", function () {
                const currentInput = this;
                const oldValue = normalizeNumber(currentInput.dataset.beforeEditValue || currentInput.dataset.originalValue);
                const newValue = normalizeNumber(currentInput.value);

                if (!oldValue || !newValue || oldValue === newValue) {
                    currentInput.dataset.beforeEditValue = currentInput.value;
                    currentInput.dataset.originalValue = currentInput.value;
                    return;
                }

                const allInputs = Array.from(document.querySelectorAll(".part1-order-input"));

                const targetInput = allInputs.find(other => {
                    return other !== currentInput && normalizeNumber(other.value) === newValue;
                });

                if (targetInput) {
                    targetInput.value = oldValue;
                    targetInput.dataset.originalValue = oldValue;
                    targetInput.dataset.beforeEditValue = oldValue;

                    const targetRow = targetInput.closest("tr");
                    if (targetRow) {
                        targetRow.style.outline = "3px solid #e60023";
                        targetRow.style.outlineOffset = "-3px";
                        setTimeout(() => {
                            targetRow.style.outline = "";
                            targetRow.style.outlineOffset = "";
                        }, 900);
                    }
                }

                currentInput.dataset.originalValue = newValue;
                currentInput.dataset.beforeEditValue = newValue;

                const currentRow = currentInput.closest("tr");
                if (currentRow) {
                    currentRow.style.outline = "3px solid #ff5f76";
                    currentRow.style.outlineOffset = "-3px";
                    setTimeout(() => {
                        currentRow.style.outline = "";
                        currentRow.style.outlineOffset = "";
                    }, 900);
                }
            });
        });
    }

    document.addEventListener("DOMContentLoaded", setupInstantOrderSwap);
    window.addEventListener("load", setupInstantOrderSwap);
    setupInstantOrderSwap();
})();
</script>
'''

if 'id="part1-instant-order-swap"' not in html:
    html = html.replace("</body>", swap_js + "\n</body>")

tpl_path.write_text(html, encoding="utf-8")

print("Done: Part 1 STT now swaps instantly when you change a number.")

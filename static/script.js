
document.addEventListener("DOMContentLoaded", () => {
    const cards = [...document.querySelectorAll(".item-card")];
    const searchInput = document.getElementById("searchInput");
    const typeFilter = document.getElementById("typeFilter");
    const categoryFilter = document.getElementById("categoryFilter");
    const resultCount = document.getElementById("resultCount");
    const emptyState = document.getElementById("filterEmpty");
    const resetButton = document.getElementById("resetFilters");
    const toast = document.getElementById("toast");

    let toastTimer;

    function showToast(message) {
        toast.textContent = message;
        toast.classList.add("show");
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => toast.classList.remove("show"), 2800);
    }

    // Populate categories from real database listings.
    const categories = [...new Set(
        cards.map(card => card.dataset.category).filter(Boolean)
    )].sort();

    categories.forEach(category => {
        const option = document.createElement("option");
        option.value = category;
        option.textContent = category.charAt(0).toUpperCase() + category.slice(1);
        categoryFilter.appendChild(option);
    });

    // Default the report date to today, using the local date.
    const dateInput = document.getElementById("date");
    if (dateInput && !dateInput.value) {
        const now = new Date();
        const localDate = [
            now.getFullYear(),
            String(now.getMonth() + 1).padStart(2, "0"),
            String(now.getDate()).padStart(2, "0")
        ].join("-");
        dateInput.value = localDate;
    }

    function filterCards() {
        const query = searchInput.value.trim().toLowerCase();
        const type = typeFilter.value;
        const category = categoryFilter.value;
        let visible = 0;

        cards.forEach(card => {
            const searchableText = [
                card.dataset.title,
                card.dataset.description,
                card.dataset.location,
                card.dataset.category
            ].join(" ");

            const matchesSearch = searchableText.includes(query);
            const matchesCategory =
                category === "all" || card.dataset.category === category;

            let matchesType = true;

            if (type === "lost" || type === "found") {
                matchesType = card.dataset.kind === type &&
                              card.dataset.status === "active";
            } else if (type === "recovered") {
                matchesType = card.dataset.status === "recovered";
            }

            const show = matchesSearch && matchesCategory && matchesType;
            card.hidden = !show;

            if (show) visible++;
        });

        resultCount.textContent =
            `${visible} listing${visible === 1 ? "" : "s"}`;

        emptyState.hidden = visible !== 0;
    }

    searchInput.addEventListener("input", filterCards);
    typeFilter.addEventListener("change", filterCards);
    categoryFilter.addEventListener("change", filterCards);

    resetButton.addEventListener("click", () => {
        searchInput.value = "";
        typeFilter.value = "all";
        categoryFilter.value = "all";
        filterCards();
        showToast("Filters cleared ✨");
    });

    document.getElementById("searchForm").addEventListener("submit", event => {
        // Let Flask handle the submitted search query.
        if (!searchInput.value.trim()) {
            event.preventDefault();
            history.replaceState(null, "", "/");
            filterCards();
        }
    });

    // Give feedback before submitting real forms to Flask.
    document.getElementById("addForm").addEventListener("submit", event => {
        if (!event.currentTarget.checkValidity()) return;

        event.preventDefault();
        const form = event.currentTarget;
        showToast("Publishing your listing… ✨");

        setTimeout(() => HTMLFormElement.prototype.submit.call(form), 350);
    });

    document.querySelectorAll(".recover-form").forEach(form => {
        form.addEventListener("submit", event => {
            event.preventDefault();

            if (!confirm("Mark this item as recovered?")) return;

            showToast("Updating item status… ✓");
            setTimeout(() => HTMLFormElement.prototype.submit.call(form), 350);
        });
    });

    filterCards();
});

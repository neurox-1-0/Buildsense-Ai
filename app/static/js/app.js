

document.addEventListener("DOMContentLoaded", () => {
    initializeActiveNavigation();
    initializeFlashMessages();
    initializeFormLoadingStates();
    initializeDecisionConfirmations();
    initializeCharacterCounters();
    initializeAutoResizeTextareas();
    initializeExpandableSections();
    initializeExternalLinks();
    initializeKeyboardShortcuts();
    initializeOpportunityScenarios();
    initializeOpportunityFilters();
    initializeSourceCounter();
    initializeRecordDeletion();
});

/* Navigation */

/**
 * Adds an active class to navigation links that match
 * the current page URL.
 */
function initializeActiveNavigation() {
    const currentPath = window.location.pathname;
    const navigationLinks = document.querySelectorAll(".nav-link");

    navigationLinks.forEach((link) => {
        const linkUrl = new URL(link.href, window.location.origin);
        const linkPath = linkUrl.pathname;

        const isExactMatch = linkPath === currentPath;
        const isSectionMatch =
            linkPath !== "/" &&
            currentPath.startsWith(linkPath);

        if (isExactMatch || isSectionMatch) {
            link.classList.add("active");
            link.setAttribute("aria-current", "page");
        }
    });
}

/* 
   Flash Messages
 */

/**
 * Adds close behavior and automatic removal to Flask
 * flash messages.
 */
function initializeFlashMessages() {
    const flashMessages = document.querySelectorAll(".flash");

    flashMessages.forEach((flash, index) => {
        const closeButton = flash.querySelector(".flash-close");

        if (closeButton) {
            closeButton.addEventListener("click", () => {
                hideElement(flash);
            });
        }

        const autoDismissDisabled =
            flash.dataset.autoDismiss === "false";

        if (!autoDismissDisabled) {
            const delay = 5000 + index * 300;

            window.setTimeout(() => {
                if (document.body.contains(flash)) {
                    hideElement(flash);
                }
            }, delay);
        }
    });
}

/**
 * Hides an element with an animation before removing it.
 *
 * @param {HTMLElement} element
 */
function hideElement(element) {
    element.classList.add("is-hiding");

    window.setTimeout(() => {
        element.remove();
    }, 260);
}

/* 
   Form Submission Loading State
 */

/**
 * Prevents duplicate form submission and displays a loading
 * state on the clicked submit button.
 */
function initializeFormLoadingStates() {
    const forms = document.querySelectorAll("form");

    forms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (!form.checkValidity()) {
                return;
            }

            const submitter = event.submitter;

            if (!(submitter instanceof HTMLButtonElement)) {
                return;
            }

            if (submitter.dataset.skipLoading === "true") {
                return;
            }

            window.setTimeout(() => {
                setButtonLoading(submitter, true);

                const submitButtons = form.querySelectorAll(
                    'button[type="submit"], button:not([type])'
                );

                submitButtons.forEach((button) => {
                    if (button !== submitter) {
                        button.disabled = true;
                    }
                });
            }, 10);
        });
    });
}

/**
 * Sets or clears a button loading state.
 *
 * @param {HTMLButtonElement} button
 * @param {boolean} loading
 */
function setButtonLoading(button, loading) {
    if (loading) {
        button.dataset.originalText = button.innerHTML;
        button.classList.add("loading-button");
        button.disabled = true;
        button.setAttribute("aria-busy", "true");
    } else {
        button.classList.remove("loading-button");
        button.disabled = false;
        button.removeAttribute("aria-busy");

        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
    }
}

/* 
   Human Decision Confirmations
 */

/**
 * Adds confirmation dialogs to sensitive recommendation
 * decision actions.
 */
function initializeDecisionConfirmations() {
    const decisionButtons = document.querySelectorAll(
        '.decision-button[name="action"], ' +
        '.button-row button[name="action"]'
    );

    const confirmationMessages = {
        approve:
            "Approve this recommendation and record it as the final business decision?",
        modify:
            "Approve the modified recommendation summary?",
        request_analysis:
            "Request additional analysis? The agents may collect and analyze more evidence.",
        reject:
            "Reject this recommendation? This decision will be recorded in the decision trail.",
        restart:
            "Restart the complete autonomous workflow for this objective?"
    };

    decisionButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
            const action = button.value;
            const message = confirmationMessages[action];

            if (!message) {
                return;
            }

            if (action === "modify") {
                const modifiedSummary = document.querySelector(
                    'textarea[name="modified_summary"]'
                );

                if (
                    modifiedSummary &&
                    modifiedSummary.value.trim().length === 0
                ) {
                    event.preventDefault();

                    showToast(
                        "Enter a modified recommendation summary before approving.",
                        "warning"
                    );

                    modifiedSummary.focus();
                    return;
                }
            }

            if (
                action === "request_analysis" ||
                action === "reject"
            ) {
                const feedback = document.querySelector(
                    'textarea[name="feedback"]'
                );

                if (
                    feedback &&
                    feedback.value.trim().length === 0
                ) {
                    event.preventDefault();

                    showToast(
                        "Add feedback explaining this decision.",
                        "warning"
                    );

                    feedback.focus();
                    return;
                }
            }

            const confirmed = window.confirm(message);

            if (!confirmed) {
                event.preventDefault();
            }
        });
    });
}

/* 
   Textarea Auto Resize
 */

/**
 * Automatically adjusts textarea height based on content.
 */
function initializeAutoResizeTextareas() {
    const textareas = document.querySelectorAll("textarea");

    textareas.forEach((textarea) => {
        autoResizeTextarea(textarea);

        textarea.addEventListener("input", () => {
            autoResizeTextarea(textarea);
        });
    });
}

/**
 * Resizes one textarea.
 *
 * @param {HTMLTextAreaElement} textarea
 */
function autoResizeTextarea(textarea) {
    const minimumHeight = Number(
        textarea.dataset.minHeight || 92
    );

    textarea.style.height = "auto";

    textarea.style.height = `${Math.max(
        textarea.scrollHeight,
        minimumHeight
    )}px`;
}

/* 
   Character Counters
 */


function initializeCharacterCounters() {
    const fields = document.querySelectorAll(
        "textarea[maxlength], input[maxlength]"
    );

    fields.forEach((field) => {
        const maximumLength = Number(field.maxLength);

        if (!Number.isFinite(maximumLength)) {
            return;
        }

        const counter = document.createElement("small");

        counter.className = "form-help character-counter";
        counter.setAttribute("aria-live", "polite");

        field.insertAdjacentElement("afterend", counter);

        const updateCounter = () => {
            const currentLength = field.value.length;

            counter.textContent =
                `${currentLength} / ${maximumLength}`;

            counter.style.color =
                currentLength >= maximumLength
                    ? "var(--danger-700)"
                    : "";
        };

        field.addEventListener("input", updateCounter);
        updateCounter();
    });
}

/* 
   Details and Expandable Sections
 */

/**
 * Closes other expandable trail or alternative sections
 * when one section is opened.
 */
function initializeExpandableSections() {
    const expandableSections = document.querySelectorAll(
        ".trail-data, .alternative-details"
    );

    expandableSections.forEach((section) => {
        section.addEventListener("toggle", () => {
            if (!section.open) {
                return;
            }

            expandableSections.forEach((otherSection) => {
                if (
                    otherSection !== section &&
                    otherSection.open &&
                    otherSection.parentElement ===
                        section.parentElement
                ) {
                    otherSection.open = false;
                }
            });
        });
    });
}

/* 
   External Links
 */

/**
 * Secures links that open in a new tab.
 */
function initializeExternalLinks() {
    const externalLinks = document.querySelectorAll(
        'a[target="_blank"]'
    );

    externalLinks.forEach((link) => {
        const existingRel = link.getAttribute("rel") || "";
        const relValues = new Set(existingRel.split(/\s+/));

        relValues.add("noopener");
        relValues.add("noreferrer");

        link.setAttribute(
            "rel",
            Array.from(relValues).filter(Boolean).join(" ")
        );
    });
}

/* 
   Toast Notifications
 */

/**
 * Creates a temporary toast notification.
 *
 * @param {string} message
 * @param {"success"|"error"|"warning"|"info"} type
 * @param {number} duration
 */
function showToast(
    message,
    type = "info",
    duration = 4200
) {
    let container = document.querySelector(".toast-container");

    if (!container) {
        container = document.createElement("div");
        container.className = "toast-container";
        container.setAttribute("aria-live", "polite");
        container.setAttribute("aria-atomic", "true");

        document.body.appendChild(container);
    }

    const toast = document.createElement("div");

    toast.className = `toast toast-${type}`;
    toast.setAttribute("role", "status");

    const icon = document.createElement("span");
    icon.setAttribute("aria-hidden", "true");

    const icons = {
        success: "✓",
        error: "!",
        warning: "⚠",
        info: "i"
    };

    icon.textContent = icons[type] || icons.info;

    const text = document.createElement("span");
    text.textContent = message;

    toast.append(icon, text);
    container.appendChild(toast);

    window.setTimeout(() => {
        toast.classList.add("is-hiding");

        window.setTimeout(() => {
            toast.remove();

            if (container.children.length === 0) {
                container.remove();
            }
        }, 260);
    }, duration);
}

/* 
   Page Loading Overlay
 */

/**
 * Displays a full-page loading overlay.
 *
 * @param {string} message
 */
function showPageLoading(
    message = "Processing request..."
) {
    let overlay = document.querySelector(
        ".page-loading-overlay"
    );

    if (!overlay) {
        overlay = document.createElement("div");
        overlay.className = "page-loading-overlay";

        overlay.innerHTML = `
            <div class="page-loading-card" role="status">
                <span class="inline-spinner" aria-hidden="true"></span>
                <span class="page-loading-message"></span>
            </div>
        `;

        document.body.appendChild(overlay);
    }

    const messageElement = overlay.querySelector(
        ".page-loading-message"
    );

    if (messageElement) {
        messageElement.textContent = message;
    }

    document.body.classList.add("loading");
    overlay.classList.add("active");
}

/**
 * Removes the full-page loading overlay.
 */
function hidePageLoading() {
    const overlay = document.querySelector(
        ".page-loading-overlay"
    );

    if (!overlay) {
        return;
    }

    document.body.classList.remove("loading");
    overlay.classList.remove("active");
}

/* 
   Auto Refresh Helper
 */


function initializeAutoRefreshFromDataAttribute() {
    const refreshElement = document.querySelector(
        "[data-auto-refresh]"
    );

    if (!refreshElement) {
        return;
    }

    const interval = Number(
        refreshElement.dataset.autoRefresh
    );

    if (
        !Number.isFinite(interval) ||
        interval < 1000
    ) {
        return;
    }

    window.setTimeout(() => {
        window.location.reload();
    }, interval);
}

initializeAutoRefreshFromDataAttribute();

/* 
   Keyboard Shortcuts
 */


function initializeKeyboardShortcuts() {
    document.addEventListener("keydown", (event) => {
        if (event.altKey && event.key.toLowerCase() === "d") {
            const dashboardLink =
                document.querySelector(
                    'a[href="/"], .brand, .nav-link'
                );

            if (dashboardLink) {
                window.location.href = dashboardLink.href;
            }
        }

        if (event.key === "Escape") {
            const flashMessages =
                document.querySelectorAll(".flash");

            flashMessages.forEach((flash) => {
                hideElement(flash);
            });
        }
    });
}

/* 
   Public Helpers
 */

window.BuildSenseUI = Object.freeze({
    showToast,
    showPageLoading,
    hidePageLoading,
    setButtonLoading
});

/*
   Opportunity Command Center
 */

function initializeOpportunityScenarios() {
    const selector = document.querySelector("#scenario-preset");
    const applyButton = document.querySelector("#apply-scenario");
    const form = document.querySelector("#opportunity-form");

    if (!selector || !applyButton || !form) {
        return;
    }

    const scenarios = {
        pharmacy: {
            title: "Pharmacy inventory and customer satisfaction",
            description:
                "Improve inventory planning and product strategy for a pharmacy business in Sri Lanka. Analyze customer reviews, online discussions, competitor pharmacies, and healthcare websites to determine which medicines and wellness products should be stocked over the next three months. Recommend inventory changes, marketing strategies, and operational improvements based on customer demand.",
            industry: "Pharmacy retail and healthcare",
            target_market: "Pharmacy customers in Sri Lanka",
            keywords:
                "Sri Lanka pharmacy customer reviews, medicine availability, wellness products Sri Lanka, pharmacy inventory demand",
            source_urls: ""
        },
        pizza: {
            title: "Pizza shop opportunity in Rathnapura",
            description:
                "Assess whether opening an affordable pizza shop in Rathnapura is a strong business opportunity. Analyze local competitors, customer reviews, menu pricing, delivery expectations, family demand, student demand, vegetarian options, and late-night ordering, then recommend an evidence-backed launch strategy.",
            industry: "Food and restaurant",
            target_market:
                "Students, families, and young professionals in Rathnapura",
            keywords:
                "pizza restaurant Rathnapura reviews, affordable pizza Rathnapura, food delivery Rathnapura, family restaurant Rathnapura",
            source_urls:
                "https://ordernow.lk/menu/daily-dish/\nhttps://grandamanee.com/dining"
        },
        laptop: {
            title: "University student laptop opportunity in Sri Lanka",
            description:
                "Identify evidence-backed product, pricing, warranty, and service actions a Sri Lankan computer retailer can test for university students seeking affordable laptops suitable for study and gaming.",
            industry: "Computer retail",
            target_market: "University students in Sri Lanka",
            keywords:
                "Sri Lanka student gaming laptop, affordable university laptop Sri Lanka, laptop warranty student",
            source_urls:
                "https://bestlap.lk/laptops/student\nhttps://laptopstore.lk/"
        },
        custom: {
            title: "",
            description: "",
            industry: "",
            target_market: "",
            keywords: "",
            source_urls: ""
        }
    };

    applyButton.addEventListener("click", () => {
        const scenario = scenarios[selector.value];
        if (!scenario) {
            showToast("Choose a scenario first.", "warning");
            return;
        }

        Object.entries(scenario).forEach(([name, value]) => {
            const field = form.elements.namedItem(name);
            if (field) {
                field.value = value;
                field.dispatchEvent(new Event("input", { bubbles: true }));
            }
        });

        const firstField = form.querySelector("#title");
        if (firstField) {
            firstField.focus();
        }
        showToast(
            selector.value === "custom"
                ? "Blank opportunity form ready."
                : "Scenario loaded. Review it before starting.",
            "success"
        );
    });
}

function initializeOpportunityFilters() {
    const filters = document.querySelectorAll("[data-status-filter]");
    const rows = document.querySelectorAll("[data-opportunity-status]");
    const empty = document.querySelector("#filter-empty");

    if (!filters.length || !rows.length) {
        return;
    }

    filters.forEach((filter) => {
        filter.addEventListener("click", () => {
            filters.forEach((item) => item.classList.remove("active"));
            filter.classList.add("active");
            const selected = filter.dataset.statusFilter;
            let visible = 0;

            rows.forEach((row) => {
                const status = row.dataset.opportunityStatus || "";
                const activeMatch =
                    selected === "running" &&
                    ["queued", "running", "cancel_requested"].includes(status);
                const approvedMatch =
                    selected === "approved" &&
                    ["approved", "approved_with_modification"].includes(status);
                const show =
                    selected === "all" ||
                    status === selected ||
                    activeMatch ||
                    approvedMatch;
                row.hidden = !show;
                if (show) {
                    visible += 1;
                }
            });

            if (empty) {
                empty.hidden = visible !== 0;
            }
        });
    });
}

function initializeSourceCounter() {
    const sourceField = document.querySelector("#source_urls");
    const counter = document.querySelector("#source-count");

    if (!sourceField || !counter) {
        return;
    }

    const update = () => {
        const count = sourceField.value
            .split(/\r?\n/)
            .map((value) => value.trim())
            .filter(Boolean).length;
        counter.textContent = `${count} ${count === 1 ? "source" : "sources"}`;
    };

    sourceField.addEventListener("input", update);
    update();
}

function initializeRecordDeletion() {
    const forms = document.querySelectorAll(".record-delete-form");
    const dialog = document.querySelector("#delete-dialog");
    if (!forms.length || !(dialog instanceof HTMLDialogElement)) {
        return;
    }

    const message = dialog.querySelector("#delete-dialog-message");
    const cancel = dialog.querySelector(".dialog-cancel");
    const confirm = dialog.querySelector(".dialog-confirm");
    let pendingForm = null;

    forms.forEach((form) => {
        form.addEventListener("submit", (event) => {
            if (form.dataset.confirmed === "true") return;
            event.preventDefault();
            pendingForm = form;
            const title = form.dataset.recordTitle || "this opportunity";
            message.textContent =
                `"${title}" and all reports, evidence, executions, and ` +
                "decision history will be permanently removed.";
            dialog.showModal();
        });
    });

    cancel.addEventListener("click", () => {
        pendingForm = null;
        dialog.close();
    });
    confirm.addEventListener("click", () => {
        if (!pendingForm) return dialog.close();
        const form = pendingForm;
        pendingForm = null;
        form.dataset.confirmed = "true";
        dialog.close();
        form.requestSubmit();
    });
    dialog.addEventListener("click", (event) => {
        if (event.target === dialog) {
            pendingForm = null;
            dialog.close();
        }
    });
}

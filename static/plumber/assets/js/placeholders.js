(function () {
    "use strict";

    var photoPathPattern = /\/static\/plumber\/assets\/images\/(resource|gallery|background|main-slider)\//i;

    function imageSizeLabel(width, height) {
        width = Math.round(width || 0);
        height = Math.round(height || 0);
        return width && height ? width + " x " + height : "Image size";
    }

    function markImage(img) {
        if (!img || img.dataset.placeholderProcessed === "true" || !photoPathPattern.test(img.getAttribute("src") || "")) {
            return;
        }

        if (img.closest && img.closest(".project-album")) {
            return;
        }

        img.dataset.placeholderProcessed = "true";

        var rect = img.getBoundingClientRect();
        var naturalWidth = img.naturalWidth || rect.width || img.width;
        var naturalHeight = img.naturalHeight || rect.height || img.height;
        var frame = img.parentElement;
        if (!frame) {
            return;
        }

        frame.classList.add("photo-placeholder-frame");
        frame.dataset.placeholderSize = imageSizeLabel(naturalWidth, naturalHeight);
    }

    function processImages(root) {
        var scope = root || document;
        var images = [];
        if (scope.matches && scope.matches("img")) {
            images.push(scope);
        }
        Array.prototype.push.apply(images, scope.querySelectorAll ? scope.querySelectorAll("img") : []);

        images.forEach(function (img) {
            if (img.complete) {
                markImage(img);
            } else {
                img.addEventListener("load", function () {
                    markImage(img);
                }, { once: true });
            }
        });
    }

    function processBackgrounds(root) {
        var scope = root || document;
        var elements = [];
        if (scope.matches && scope.matches("[style*='/static/plumber/assets/images/']")) {
            elements.push(scope);
        }
        Array.prototype.push.apply(elements, scope.querySelectorAll ? scope.querySelectorAll("[style*='/static/plumber/assets/images/']") : []);

        elements.forEach(function (element) {
            var style = element.getAttribute("style") || "";
            if (!photoPathPattern.test(style)) {
                return;
            }

            var rect = element.getBoundingClientRect();
            element.classList.add("photo-background-placeholder");
            element.dataset.placeholderSize = imageSizeLabel(rect.width, rect.height);
        });
    }

    function removeGeneratedOwlStageClass() {
        Array.prototype.forEach.call(document.querySelectorAll(".owl-stage-outer"), function (element) {
            element.classList.add("carousel-viewport");
            element.classList.remove("owl-stage-outer");
        });
    }

    function processPage() {
        processImages(document);
        processBackgrounds(document);
        removeGeneratedOwlStageClass();
    }

    function observePageChanges() {
        if (!("MutationObserver" in window)) {
            return;
        }

        var observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.type === "attributes") {
                    removeGeneratedOwlStageClass();
                    return;
                }

                Array.prototype.forEach.call(mutation.addedNodes, function (node) {
                    if (node.nodeType !== 1) {
                        return;
                    }

                    processImages(node);
                    processBackgrounds(node);
                    removeGeneratedOwlStageClass();
                });
            });
        });

        observer.observe(document.documentElement, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ["class"]
        });
    }

    function setupProjectModal() {
        var modal = document.getElementById("projectModal");
        if (!modal || !window.jQuery) {
            return;
        }

        var albumImages = [];
        var currentAlbumIndex = 0;
        var album = document.getElementById("projectModalAlbum");

        function escapeAttribute(value) {
            return String(value || "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }

        function renderAlbum(title) {
            if (!album) {
                return;
            }

            var image = albumImages[currentAlbumIndex] || "/static/plumber/assets/images/gallery/image-1.jpg";
            var controls = albumImages.length > 1 ? [
                '<button type="button" class="project-album-arrow project-album-prev" aria-label="Previous image">&larr;</button>',
                '<button type="button" class="project-album-arrow project-album-next" aria-label="Next image">&rarr;</button>',
                '<div class="project-album-counter">' + (currentAlbumIndex + 1) + ' / ' + albumImages.length + '</div>'
            ].join("") : "";

            album.innerHTML = '<img src="' + escapeAttribute(image) + '" alt="' + escapeAttribute(title) + '">' + controls;
        }

        function parseAlbum(rawValue, fallbackImage) {
            var parsed = [];
            try {
                parsed = JSON.parse(rawValue || "[]");
            } catch (error) {
                parsed = [];
            }

            parsed = parsed.filter(function (src) {
                return typeof src === "string" && src.length;
            });

            if (!parsed.length && fallbackImage) {
                parsed.push(fallbackImage);
            }

            return parsed;
        }

        window.jQuery("#projectModal").on("show.bs.modal", function (event) {
            var trigger = event.relatedTarget;
            if (!trigger) {
                return;
            }

            var title = trigger.getAttribute("data-title") || "Project Details";
            var description = trigger.getAttribute("data-description") || "";
            var cover = trigger.getAttribute("data-cover") || "";

            albumImages = parseAlbum(trigger.getAttribute("data-images"), cover);
            currentAlbumIndex = 0;

            document.getElementById("projectModalLabel").textContent = title;
            document.getElementById("projectModalDescription").textContent = description;
            renderAlbum(title);

            processImages(modal);
        });

        album.addEventListener("click", function (event) {
            var button = event.target.closest(".project-album-arrow");
            if (!button || albumImages.length < 2) {
                return;
            }

            var title = document.getElementById("projectModalLabel").textContent;
            currentAlbumIndex += button.classList.contains("project-album-next") ? 1 : -1;
            if (currentAlbumIndex < 0) {
                currentAlbumIndex = albumImages.length - 1;
            }
            if (currentAlbumIndex >= albumImages.length) {
                currentAlbumIndex = 0;
            }

            renderAlbum(title);
            processImages(modal);
        });

        Array.prototype.forEach.call(document.querySelectorAll(".portfolio-section .gallery-block .inner-box"), function (card) {
            card.addEventListener("keydown", function (event) {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    window.jQuery("#projectModal").modal("show", card);
                }
            });
        });
    }

    function setupRequestModal() {
        if (!window.jQuery || !document.getElementById("requestModal")) {
            return;
        }

        var requestLabels = {
            standard: "Standard Request",
            urgent: "Urgent Request",
            commercial: "Commercial B2B Clients",
            complex: "High Complexity Request"
        };

        window.jQuery("#requestModal").on("show.bs.modal", function (event) {
            var trigger = event.relatedTarget;
            var requestType = trigger ? trigger.getAttribute("data-request-type") : "";
            var requestLabel = requestLabels[requestType] || "Request a Quote";
            var title = document.getElementById("requestModalLabel");
            var select = this.querySelector("select[name='subject']");

            if (title) {
                title.textContent = requestLabel;
            }

            if (select && requestType) {
                select.value = requestType;
            }
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", processPage);
    } else {
        processPage();
    }

    observePageChanges();
    setupProjectModal();
    setupRequestModal();

    window.addEventListener("load", function () {
        processPage();
        setTimeout(processPage, 300);
    });
}());

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

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", processPage);
    } else {
        processPage();
    }

    observePageChanges();

    window.addEventListener("load", function () {
        processPage();
        setTimeout(processPage, 300);
    });
}());

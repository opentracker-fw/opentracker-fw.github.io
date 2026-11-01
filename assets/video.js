/* Click-to-play: the YouTube player loads only after a click. */
document.querySelectorAll(".yt[data-id]").forEach(function (el) {
  el.addEventListener("click", function (e) {
    e.preventDefault();
    var f = document.createElement("iframe");
    f.src = "https://www.youtube-nocookie.com/embed/" + el.dataset.id + "?autoplay=1&rel=0";
    f.title = el.dataset.title || "Video";
    f.allow = "autoplay; encrypted-media; picture-in-picture; fullscreen";
    f.allowFullscreen = true;
    el.replaceWith(f);
    f.parentNode.classList.add("playing");
  });
});

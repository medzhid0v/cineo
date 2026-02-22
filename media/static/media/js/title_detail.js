document.addEventListener("DOMContentLoaded", () => {
    // AJAX для переключения эпизодов
    document.querySelectorAll(".episode-toggle-form").forEach((form) => {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const btn = form.querySelector(".episode-btn");
            if (!btn) return;

            const watched = btn.dataset.watched === "1";

            const formData = new FormData(form);
            formData.set("watched", watched ? "0" : "1");

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: formData,
                    headers: {"X-Requested-With": "XMLHttpRequest"},
                });

                if (!response.ok) return;

                const data = await response.json();

                btn.dataset.watched = data.watched ? "1" : "0";
                btn.textContent = data.watched ? "✓ Просмотрено" : "Отметить";

                const hidden = form.querySelector('input[name="watched"]');
                if (hidden) hidden.value = data.watched ? "0" : "1";

                if (data.watched_episodes !== undefined && data.total_episodes !== undefined) {
                    const progressCount = document.querySelector(".progress-count");
                    if (progressCount) {
                        progressCount.textContent = `${data.watched_episodes}/${data.total_episodes} эпизодов`;
                    }
                }

                const currentEpisode = document.querySelector(".current-episode");
                if (currentEpisode) {
                    if (data.current_season_number && data.current_episode_number) {
                        currentEpisode.textContent =
                            `Сезон ${data.current_season_number}, Серия ${data.current_episode_number}`;
                    } else {
                        currentEpisode.textContent = "—";
                    }
                }
            } catch (error) {
                console.error("Ошибка при обновлении эпизода:", error);
            }
        });
    });

    // AJAX для удаления
    const removeForm = document.querySelector(".remove-form");
    if (removeForm) {
        removeForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            if (!confirm("Удалить из списка?")) return;

            const redirectUrl = removeForm.dataset.redirectUrl || "/";
            const formData = new FormData(removeForm);

            try {
                const response = await fetch(removeForm.action, {
                    method: "POST",
                    body: formData,
                    headers: {"X-Requested-With": "XMLHttpRequest"},
                });

                if (response.ok) {
                    window.location.href = redirectUrl;
                }
            } catch (error) {
                console.error("Ошибка при удалении:", error);
            }
        });
    }
});

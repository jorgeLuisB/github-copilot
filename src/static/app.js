document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  function showMessage(text, type) {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");

    setTimeout(() => {
      messageDiv.classList.add("hidden");
    }, 5000);
  }

  async function fetchActivities() {
    try {
      const response = await fetch(`/activities?cacheBust=${Date.now()}`, {
        cache: "no-store",
      });
      const activities = await response.json();

      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        const participantsList = document.createElement("ul");
        participantsList.className = "participants-list";

        if (details.participants.length === 0) {
          const emptyItem = document.createElement("li");
          emptyItem.className = "participants-empty";
          emptyItem.textContent = "No participants yet.";
          participantsList.appendChild(emptyItem);
        } else {
          details.participants.forEach((participant) => {
            const participantItem = document.createElement("li");
            participantItem.className = "participant-item";

            const participantName = document.createElement("span");
            participantName.textContent = participant;

            const removeButton = document.createElement("button");
            removeButton.type = "button";
            removeButton.className = "remove-participant";
            removeButton.textContent = "✕";
            removeButton.title = `Remove ${participant} from ${name}`;
            removeButton.setAttribute("aria-label", `Remove ${participant} from ${name}`);
            removeButton.addEventListener("click", async () => {
              try {
                const deleteResponse = await fetch(
                  `/activities/${encodeURIComponent(name)}/signup?email=${encodeURIComponent(participant)}`,
                  { method: "DELETE", cache: "no-store" }
                );
                const deleteResult = await deleteResponse.json();

                if (deleteResponse.ok) {
                  showMessage(deleteResult.message, "success");
                  await fetchActivities();
                } else {
                  showMessage(deleteResult.detail || "Could not remove participant.", "error");
                }
              } catch (error) {
                console.error("Error removing participant:", error);
                showMessage("Failed to remove participant.", "error");
              }
            });

            participantItem.append(participantName, removeButton);
            participantsList.appendChild(participantItem);
          });
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        `;

        const participantSection = document.createElement("div");
        participantSection.className = "participant-section";

        const participantHeading = document.createElement("p");
        participantHeading.className = "participant-heading";
        participantHeading.innerHTML = "<strong>Participants:</strong>";

        participantSection.appendChild(participantHeading);
        participantSection.appendChild(participantsList);
        activityCard.appendChild(participantSection);

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
          cache: "no-store",
        }
      );

      const result = await response.json();

      if (response.ok) {
        showMessage(result.message, "success");
        await fetchActivities();
        signupForm.reset();
      } else {
        showMessage(result.detail || "An error occurred", "error");
      }
    } catch (error) {
      showMessage("Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  fetchActivities();
});


const refreshBtn = document.getElementById("refreshBtn");
const statusText = document.getElementById("status");

async function loadDashboard() {
    statusText.textContent = "Loading analytics...";
    refreshBtn.disabled = true;

    try {
        const response = await fetch("/api/analytics/summary");

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();

        document.getElementById("totalMembers").textContent =
            data.total_members ?? 0;

        document.getElementById("totalRevenue").textContent =
            new Intl.NumberFormat("en-IN", {
                style: "currency",
                currency: "INR",
                maximumFractionDigits: 2
            }).format(data.total_revenue ?? 0);

        document.getElementById("activeMemberships").textContent =
            data.active_memberships ?? 0;

        document.getElementById("attendanceRecords").textContent =
            data.total_attendance_records ?? 0;

        document.getElementById("totalPlans").textContent =
            data.total_workout_plans ?? 0;

        document.getElementById("completedWorkouts").textContent =
            data.completed_workouts ?? 0;

        document.getElementById("pendingWorkouts").textContent =
            data.pending_workouts ?? 0;

        document.getElementById("progressRecords").textContent =
            data.total_workout_progress_records ?? 0;

        const rate = Math.min(
            100,
            Math.max(0, Number(data.workout_completion_rate) || 0)
        );

        document.getElementById("completionRate").textContent = `${rate}%`;

        document.getElementById("progressRing").style.background =
            `conic-gradient(#7158e2 ${rate}%, #eeeef5 ${rate}%)`;

        document.getElementById("uniqueAttendees").textContent =
            data.unique_members_attended ?? 0;

        // Render membership plan distribution
        const plans = data.membership_plan_distribution ?? {};
        const planContainer = document.getElementById("planDistribution");
        const entries = Object.entries(plans);
        const maxCount = Math.max(1, ...entries.map(([, count]) => count));

        planContainer.replaceChildren();

        if (entries.length === 0) {
            const message = document.createElement("p");
            message.textContent = "No membership plans recorded yet.";
            planContainer.appendChild(message);
        } else {
            entries.forEach(([name, count]) => {
                const row = document.createElement("div");
                row.className = "plan-row";

                const label = document.createElement("div");
                label.className = "plan-label";

                const planName = document.createElement("span");
                planName.textContent = name;

                const planCount = document.createElement("strong");
                planCount.textContent = count;

                label.append(planName, planCount);

                const track = document.createElement("div");
                track.className = "plan-track";

                const bar = document.createElement("div");
                bar.className = "plan-bar";
                bar.style.width = `${(count / maxCount) * 100}%`;

                track.appendChild(bar);
                row.append(label, track);
                planContainer.appendChild(row);
            });
        }

        statusText.textContent =
            `Analytics updated successfully at ${new Date().toLocaleTimeString()}.`;
    } catch (error) {
        console.error("Dashboard loading failed:", error);
        statusText.textContent =
            "Could not load analytics. Check that Flask is running.";
    } finally {
        refreshBtn.disabled = false;
    }
}

refreshBtn.addEventListener("click", loadDashboard);
loadDashboard();

const refreshMembersBtn = document.getElementById("refreshMembersBtn");
const membersStatus = document.getElementById("membersStatus");
const membersTableBody = document.getElementById("membersTableBody");

async function loadMembers() {
    membersStatus.textContent = "Loading members...";
    refreshMembersBtn.disabled = true;

    membersTableBody.replaceChildren();

    const loadingRow = document.createElement("tr");
    const loadingCell = document.createElement("td");
    loadingCell.colSpan = 7;
    loadingCell.textContent = "Loading members...";
    loadingRow.appendChild(loadingCell);
    membersTableBody.appendChild(loadingRow);

    try {
        const response = await fetch("/api/members");

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const result = await response.json();

        // Support either a JSON array or an object containing members.
        const members = Array.isArray(result)
            ? result
            : Array.isArray(result.members)
                ? result.members
                : null;

        if (!members) {
            throw new Error("Unexpected members API response format.");
        }

        membersTableBody.replaceChildren();

        if (members.length === 0) {
            const row = document.createElement("tr");
            const cell = document.createElement("td");

            cell.colSpan = 7;
            cell.textContent = "No members found. Add a member to get started.";

            row.appendChild(cell);
            membersTableBody.appendChild(row);

            membersStatus.textContent = "No registered members yet.";
            return;
        }

        members.forEach((member) => {
            const row = document.createElement("tr");

            const values = [
                member.id,
                member.name,
                member.age,
                member.gender,
                member.weight,
                member.fitness_goal,
                member.join_date
            ];

            values.forEach((value) => {
                const cell = document.createElement("td");

                cell.textContent =
                    value === null || value === undefined || value === ""
                        ? "—"
                        : String(value);

                row.appendChild(cell);
            });

            membersTableBody.appendChild(row);
        });

        membersStatus.textContent =
            `${members.length} member${members.length === 1 ? "" : "s"} loaded successfully.`;
    } catch (error) {
        console.error("Failed to load members:", error);

        membersTableBody.replaceChildren();

        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 7;
        cell.textContent = "Unable to load members. Please try refreshing.";

        row.appendChild(cell);
        membersTableBody.appendChild(row);

        membersStatus.textContent =
            "Could not load members. Check the API response and Flask server.";
    } finally {
        refreshMembersBtn.disabled = false;
    }
}

refreshMembersBtn.addEventListener("click", loadMembers);

// Load the members list when the dashboard opens.
loadMembers();

const addMemberBtn = document.getElementById("addMemberBtn");
const cancelMemberBtn = document.getElementById("cancelMemberBtn");
const memberFormContainer = document.getElementById("memberFormContainer");
const addMemberForm = document.getElementById("addMemberForm");
const memberFormMessage = document.getElementById("memberFormMessage");

addMemberBtn.addEventListener("click", () => {
    memberFormContainer.hidden = false;
    document.getElementById("memberJoinDate").value =
        new Date().toLocaleDateString("en-CA");
    document.getElementById("memberName").focus();
});

cancelMemberBtn.addEventListener("click", () => {
    addMemberForm.reset();
    memberFormContainer.hidden = true;
    memberFormMessage.textContent = "";
});

addMemberForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const formData = new FormData(addMemberForm);

    const memberData = {
        name: formData.get("name").trim(),
        age: Number(formData.get("age")),
        gender: formData.get("gender"),
        weight: Number(formData.get("weight")),
        fitness_goal: formData.get("fitness_goal"),
        join_date: formData.get("join_date")
    };

    memberFormMessage.textContent = "Saving member...";

    try {
        const response = await fetch("/api/members", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(memberData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Could not add member.");
        }

        memberFormMessage.textContent =
            result.message || "Member added successfully!";

        addMemberForm.reset();
        memberFormContainer.hidden = true;

        await Promise.all([
            loadMembers(),
            loadDashboard()
        ]);

    } catch (error) {
        memberFormMessage.textContent = error.message ||
            "Something went wrong. Please try again.";
    }
});

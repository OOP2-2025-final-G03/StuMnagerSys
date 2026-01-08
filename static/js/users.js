document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("user-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const data = {
      user_id: document.getElementById("user_id").value,
      name: document.getElementById("name").value,
      birth_date: document.getElementById("birth_date").value,
      role: document.getElementById("role").value,
      department: document.getElementById("department").value,
      password: document.getElementById("password").value
    };

    try {
      const res = await fetch("user/create", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + localStorage.getItem("token")
        },
        body: JSON.stringify(data)
      });

      const result = await res.json();

      if (!res.ok) {
        const errorMsg =
            result.description || result.error || "登録に失敗しました";
        throw new Error(errorMsg);
      }

      document.getElementById("message").textContent = "ユーザーを登録しました";
      form.reset();

    } catch (err) {
      document.getElementById("message").textContent = err.message;
    }
  });
});

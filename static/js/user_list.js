document.addEventListener("click", async (e) => {
  if (!e.target.closest(".delete-link")) return;

  const link = e.target.closest(".delete-link");
  const userId = link.dataset.userId;

  if (!confirm("本当に削除しますか？")) return;

  const res = await fetch(`/user/delete/${userId}`, {
    method: "POST",
    headers: {
      "Authorization": "Bearer " + localStorage.getItem("token")
    }
  });

  if (res.ok) {
    location.reload();
  } else {
    alert("削除に失敗しました");
  }
});

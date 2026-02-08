const reciterSelect = document.getElementById("reciter");
const renderButton = document.getElementById("render");
const status = document.getElementById("status");
const preview = document.getElementById("preview");
const progressBar = document.getElementById("progress-bar");
const qualitySelect = document.getElementById("quality");

async function loadReciters() {
  const response = await fetch("/api/reciters");
  const reciters = await response.json();
  reciterSelect.innerHTML = reciters
    .map(
      (reciter) =>
        `<option value="${reciter.id}">${reciter.name}</option>`
    )
    .join("");
}

async function pollStatus(jobId) {
  const response = await fetch(`/api/status/${jobId}`);
  if (!response.ok) {
    throw new Error("تعذر جلب حالة المهمة.");
  }
  return response.json();
}

async function renderVideo() {
  status.textContent = "جارٍ تجهيز الفيديو...";
  renderButton.disabled = true;
  preview.removeAttribute("src");
  progressBar.style.width = "0%";

  const payload = {
    surah: Number(document.getElementById("surah").value),
    ayah: Number(document.getElementById("ayah").value),
    reciter: reciterSelect.value,
    quality: qualitySelect.value,
  };

  try {
    const response = await fetch("/api/render", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("تعذر إنشاء الفيديو.");
    }

    const result = await response.json();
    let done = false;
    while (!done) {
      const job = await pollStatus(result.job_id);
      status.textContent = job.message || "جارٍ المعالجة...";
      progressBar.style.width = `${job.progress ?? 0}%`;
      if (job.status === "done") {
        preview.src = job.output;
        status.textContent = `تم الإنشاء بنجاح للقارئ ${job.reciter}.`;
        done = true;
        break;
      }
      if (job.status === "failed") {
        status.textContent = job.message || "فشل إنشاء الفيديو.";
        done = true;
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 1500));
    }
  } catch (error) {
    status.textContent = "حدث خطأ أثناء المعالجة. تحقق من الخادم.";
  } finally {
    renderButton.disabled = false;
  }
}

loadReciters();
renderButton.addEventListener("click", renderVideo);

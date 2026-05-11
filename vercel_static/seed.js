import { adminEmails, firebaseConfig } from "./firebase-config.js";

const logBox = document.querySelector("#logBox");
const seedBtn = document.querySelector("#seedBtn");
const emailInput = document.querySelector("#emailInput");
const passwordInput = document.querySelector("#passwordInput");

function log(message) {
  logBox.textContent += `\n${message}`;
}

function hasFirebaseConfig() {
  return Boolean(firebaseConfig.apiKey && firebaseConfig.projectId && firebaseConfig.appId);
}

seedBtn.addEventListener("click", async () => {
  logBox.textContent = "Đang xử lý...";

  if (!hasFirebaseConfig()) {
    log("Chưa điền firebase-config.js.");
    return;
  }

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!adminEmails.includes(email)) {
    log("Email này chưa nằm trong danh sách adminEmails ở firebase-config.js.");
    return;
  }

  const [{ initializeApp }, authApi, firestoreApi] = await Promise.all([
    import("https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js"),
    import("https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js"),
    import("https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js")
  ]);

  const app = initializeApp(firebaseConfig);
  const auth = authApi.getAuth(app);
  const db = firestoreApi.getFirestore(app);

  log("Login Firebase...");
  await authApi.signInWithEmailAndPassword(auth, email, password);

  log("Đọc JSON Part 1...");
  const response = await fetch("./data/listening-part-1.json", { cache: "no-store" });
  const payload = await response.json();
  const questions = payload.questions || [];
  const chunkSize = 25;
  const chunks = [];

  for (let index = 0; index < questions.length; index += chunkSize) {
    chunks.push(questions.slice(index, index + chunkSize));
  }

  log(`Có ${questions.length} câu, chia thành ${chunks.length} chunk.`);

  for (let index = 0; index < chunks.length; index += 1) {
    const chunkId = String(index + 1).padStart(4, "0");
    await firestoreApi.setDoc(
      firestoreApi.doc(db, "listeningParts", "1", "chunks", chunkId),
      {
        part: 1,
        chunkIndex: index + 1,
        questions: chunks[index],
        updatedAt: firestoreApi.serverTimestamp()
      }
    );
    log(`Đã upload chunk ${chunkId}.`);
  }

  await firestoreApi.setDoc(
    firestoreApi.doc(db, "listeningMeta", "part1"),
    {
      part: 1,
      totalQuestions: questions.length,
      updatedAt: firestoreApi.serverTimestamp()
    }
  );

  log("Xong. Firestore đã có data Part 1.");
});

import { firebaseConfig } from "./firebase-config.js";

const LOCAL_DATA_BY_PART = {
  1: "./data/listening-part-1.json"
};

const state = {
  part: 1,
  questions: [],
  currentIndex: 0,
  selectedAnswer: "",
  checked: false,
  firebaseReady: false,
  db: null,
  auth: null,
  user: null,
  studentLabel: "TSA APTIS - CHƯA ĐĂNG NHẬP"
};

const els = {
  dataSource: document.querySelector("#dataSource"),
  securityWatermark: document.querySelector("#securityWatermark"),
  authPanel: document.querySelector("#authPanel"),
  authForm: document.querySelector("#authForm"),
  authMessage: document.querySelector("#authMessage"),
  emailInput: document.querySelector("#emailInput"),
  passwordInput: document.querySelector("#passwordInput"),
  studentBadge: document.querySelector("#studentBadge"),
  logoutBtn: document.querySelector("#logoutBtn"),
  totalCount: document.querySelector("#totalCount"),
  loadingBox: document.querySelector("#loadingBox"),
  questionCard: document.querySelector("#questionCard"),
  questionBadge: document.querySelector("#questionBadge"),
  answerStatus: document.querySelector("#answerStatus"),
  questionText: document.querySelector("#questionText"),
  audioPlayer: document.querySelector("#audioPlayer"),
  audioHint: document.querySelector("#audioHint"),
  driveLink: document.querySelector("#driveLink"),
  answerButtons: [...document.querySelectorAll(".answer-btn")],
  checkBtn: document.querySelector("#checkBtn"),
  prevBtn: document.querySelector("#prevBtn"),
  nextBtn: document.querySelector("#nextBtn"),
  resetBtn: document.querySelector("#resetBtn"),
  resultBox: document.querySelector("#resultBox"),
  correctAnswer: document.querySelector("#correctAnswer"),
  transcriptText: document.querySelector("#transcriptText"),
  questionNumbers: document.querySelector("#questionNumbers"),
  currentMeta: document.querySelector("#currentMeta"),
  partTabs: [...document.querySelectorAll("[data-part]")]
};

function hasFirebaseConfig() {
  return Boolean(firebaseConfig.apiKey && firebaseConfig.projectId && firebaseConfig.appId);
}

async function initFirebase() {
  if (!hasFirebaseConfig() || state.firebaseReady) return state.firebaseReady;

  const [{ initializeApp }, { getFirestore }, authApi] = await Promise.all([
    import("https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js"),
    import("https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js"),
    import("https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js")
  ]);

  const app = initializeApp(firebaseConfig);
  state.db = getFirestore(app);
  state.auth = authApi.getAuth(app);
  state.firebaseReady = true;
  return true;
}

function renderWatermark(label) {
  const now = new Date().toLocaleString("vi-VN");
  const text = `${label} · ${now}`;
  els.securityWatermark.innerHTML = "";

  for (let index = 0; index < 54; index += 1) {
    const span = document.createElement("span");
    span.textContent = text;
    els.securityWatermark.append(span);
  }
}

function installSecurityGuards() {
  document.documentElement.classList.add("tsa-protected");

  function block(event) {
    event.preventDefault();
    event.stopPropagation();
    return false;
  }

  ["contextmenu", "copy", "cut", "paste", "dragstart", "selectstart"].forEach((eventName) => {
    document.addEventListener(eventName, block, true);
  });

  document.addEventListener("keydown", (event) => {
    const key = String(event.key || "").toLowerCase();
    if (event.key === "F12") return block(event);
    if ((event.ctrlKey || event.metaKey) && ["s", "p", "u", "c", "x", "a"].includes(key)) return block(event);
    if (event.ctrlKey && event.shiftKey && ["i", "j", "c"].includes(key)) return block(event);
    if (event.key === "PrintScreen") return block(event);
    return true;
  }, true);

  window.addEventListener("beforeprint", block);
  setInterval(() => renderWatermark(state.studentLabel), 1000);
}

async function fetchStudentLabel(user) {
  const uid = user.uid || "NO-ID";
  const email = user.email || "NO-EMAIL";
  let fullName = user.displayName || "";
  let studentId = uid;

  try {
    const { doc, getDoc } = await import("https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js");
    const snap = await getDoc(doc(state.db, "students", uid));
    if (snap.exists()) {
      const profile = snap.data();
      fullName = profile.fullName || profile.name || fullName;
      studentId = profile.studentId || profile.id || uid;
    }
  } catch (error) {}

  if (!fullName) fullName = email.split("@")[0] || "Student";
  return `ID ${studentId} - ${fullName} - ${email}`;
}

async function setupAuthGate() {
  renderWatermark(state.studentLabel);
  installSecurityGuards();

  if (!hasFirebaseConfig()) {
    els.studentBadge.textContent = "Demo chưa cấu hình Firebase";
    return true;
  }

  await initFirebase();
  const { onAuthStateChanged, signInWithEmailAndPassword, signOut } = await import("https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js");

  els.authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    els.authMessage.textContent = "Đang đăng nhập...";
    try {
      await signInWithEmailAndPassword(state.auth, els.emailInput.value.trim(), els.passwordInput.value);
      els.authMessage.textContent = "";
    } catch (error) {
      els.authMessage.textContent = "Login không thành công. Kiểm tra email/mật khẩu.";
    }
  });

  els.logoutBtn.addEventListener("click", () => signOut(state.auth));

  return new Promise((resolve) => {
    onAuthStateChanged(state.auth, async (user) => {
      state.user = user;
      if (!user) {
        state.studentLabel = "TSA APTIS - CHƯA ĐĂNG NHẬP";
        els.studentBadge.textContent = "Chưa đăng nhập";
        els.logoutBtn.hidden = true;
        els.authPanel.hidden = false;
        renderWatermark(state.studentLabel);
        return;
      }

      state.studentLabel = await fetchStudentLabel(user);
      els.studentBadge.textContent = state.studentLabel;
      els.logoutBtn.hidden = false;
      els.authPanel.hidden = true;
      renderWatermark(state.studentLabel);
      resolve(true);
    });
  });
}

async function loadFromFirestore(part) {
  await initFirebase();
  if (!state.firebaseReady) throw new Error("Firebase chưa cấu hình");

  const { collection, getDocs, orderBy, query } = await import("https://www.gstatic.com/firebasejs/10.12.5/firebase-firestore.js");
  const chunksRef = collection(state.db, "listeningParts", String(part), "chunks");
  const snapshot = await getDocs(query(chunksRef, orderBy("chunkIndex", "asc")));
  const questions = [];

  snapshot.forEach((doc) => {
    const data = doc.data();
    if (Array.isArray(data.questions)) questions.push(...data.questions);
  });

  if (!questions.length) throw new Error("Firestore chưa có data Part này");
  return questions.sort((a, b) => Number(a.number || 0) - Number(b.number || 0));
}

async function loadFromLocalJson(part) {
  const url = LOCAL_DATA_BY_PART[part];
  if (!url) return [];
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error("Không đọc được JSON tĩnh");
  const payload = await response.json();
  return Array.isArray(payload.questions) payload.questions : [];
}

async function loadPart(part) {
  state.part = Number(part);
  state.currentIndex = 0;
  state.questions = [];
  state.selectedAnswer = "";
  state.checked = false;

  showLoading(`Đang tải Part ${state.part}...`);
  setActivePart();

  try {
    state.questions = await loadFromFirestore(state.part);
    els.dataSource.textContent = "Data Firestore";
  } catch (error) {
    state.questions = await loadFromLocalJson(state.part);
    els.dataSource.textContent = state.questions.length "Data JSON tĩnh" : "Chưa có data";
  }

  if (!state.questions.length) {
    showLoading(`Part ${state.part} chưa có data.`);
    els.totalCount.textContent = "0";
    els.questionNumbers.innerHTML = "";
    els.currentMeta.textContent = "0/0";
    return;
  }

  els.loadingBox.hidden = true;
  els.questionCard.hidden = false;
  els.totalCount.textContent = String(state.questions.length);
  renderQuestionNumbers();
  renderQuestion();
}

function showLoading(message) {
  els.loadingBox.hidden = false;
  els.loadingBox.textContent = message;
  els.questionCard.hidden = true;
}

function setActivePart() {
  els.partTabs.forEach((button) => {
    button.classList.toggle("active", Number(button.dataset.part) === state.part);
  });
}

function currentQuestion() {
  return state.questions[state.currentIndex] || {};
}

function renderQuestion() {
  const question = currentQuestion();
  state.selectedAnswer = "";
  state.checked = false;

  els.questionBadge.textContent = `Câu ${question.number || state.currentIndex + 1}`;
  els.questionText.textContent = question.question || "Question chưa có nội dung.";
  els.answerStatus.textContent = "Chưa chọn answer";
  els.answerStatus.className = "answer-status";
  els.correctAnswer.textContent = question.correctAnswer || "A";
  els.transcriptText.textContent = question.transcript || "Chưa có transcript.";
  els.resultBox.hidden = true;
  els.checkBtn.disabled = false;
  els.prevBtn.disabled = state.currentIndex === 0;
  els.nextBtn.disabled = state.currentIndex >= state.questions.length - 1;
  els.currentMeta.textContent = `${state.currentIndex + 1}/${state.questions.length}`;

  setupAudio(question);

  const options = question.options || {};
  els.answerButtons.forEach((button) => {
    const answer = button.dataset.answer;
    button.className = "answer-btn";
    button.querySelector("span").textContent = options[answer] || `Answer ${answer}`;
  });

  [...els.questionNumbers.children].forEach((button, index) => {
    button.classList.toggle("current", index === state.currentIndex);
  });
}

function setupAudio(question) {
  const fileId = question.audioDriveFileId || extractDriveFileId(question.audioDriveLink);
  const directUrl = fileId `https://drive.google.com/uc?export=download&id=${fileId}` : "";
  const driveUrl = question.audioDriveLink || (fileId `https://drive.google.com/file/d/${fileId}/view` : "#");

  els.audioPlayer.src = directUrl;
  els.audioPlayer.load();
  els.audioHint.hidden = true;
  els.driveLink.href = driveUrl;
  els.driveLink.style.pointerEvents = driveUrl === "#" "none" : "";
  els.driveLink.style.opacity = driveUrl === "#" "0.55" : "";
}

function extractDriveFileId(value) {
  const text = String(value || "");
  const patterns = [/\/file\/d\/([^/]+)/, /id=([^&]+)/, /\/d\/([^/]+)/];
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[1];
  }
  return "";
}

function renderQuestionNumbers() {
  els.questionNumbers.innerHTML = "";
  state.questions.forEach((question, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = question.number || index + 1;
    button.addEventListener("click", () => {
      state.currentIndex = index;
      renderQuestion();
    });
    els.questionNumbers.append(button);
  });
}

function selectAnswer(answer) {
  if (state.checked) return;
  state.selectedAnswer = answer;
  els.answerStatus.textContent = `Đã chọn answer ${answer}`;
  els.answerStatus.className = "answer-status";

  els.answerButtons.forEach((button) => {
    button.classList.toggle("selected", button.dataset.answer === answer);
  });
}

function checkAnswer() {
  if (!state.selectedAnswer) {
    els.answerStatus.textContent = "Hãy chọn một answer trước";
    els.answerStatus.className = "answer-status warning";
    return;
  }

  const question = currentQuestion();
  const correct = String(question.correctAnswer || "A").trim().toUpperCase();
  state.checked = true;
  els.checkBtn.disabled = true;
  els.resultBox.hidden = false;

  els.answerButtons.forEach((button) => {
    const answer = button.dataset.answer;
    button.classList.toggle("correct", answer === correct);
    button.classList.toggle("wrong", answer === state.selectedAnswer && answer !== correct);
  });

  const isCorrect = state.selectedAnswer === correct;
  els.answerStatus.textContent = isCorrect "Chính xác" : "Chưa đúng";
  els.answerStatus.className = `answer-status ${isCorrect "success" : "danger"}`;
}

function moveQuestion(delta) {
  const nextIndex = state.currentIndex + delta;
  if (nextIndex < 0 || nextIndex >= state.questions.length) return;
  state.currentIndex = nextIndex;
  renderQuestion();
}

els.partTabs.forEach((button) => {
  button.addEventListener("click", () => loadPart(button.dataset.part));
});

els.answerButtons.forEach((button) => {
  button.addEventListener("click", () => selectAnswer(button.dataset.answer));
});

els.audioPlayer.addEventListener("error", () => {
  els.audioHint.hidden = false;
});

els.checkBtn.addEventListener("click", checkAnswer);
els.prevBtn.addEventListener("click", () => moveQuestion(-1));
els.nextBtn.addEventListener("click", () => moveQuestion(1));
els.resetBtn.addEventListener("click", () => renderQuestion());

setupAuthGate().then(() => loadPart(1));

document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById("startExam");
    const examIntro = document.getElementById("exam-intro");
    const examContainer = document.getElementById("exam-container");
    const questionContainer = document.getElementById("question-container");
    const submitBtn = document.getElementById("submitQuestion");
    const completeBtn = document.getElementById("completeExam");
    const timerElement = document.getElementById("timer");
    const scoreElement = document.getElementById("score");
  
    // Thiết lập biến global
    let currentQuestionIndex = 0;
    let score = 0;
    let attemptsCurrentQuestion = 0;
    let remainingTime = 3 * 60; // 3 phút = 180 giây
    let countdown;
  
    // Bắt sự kiện khi bấm "Bắt đầu thi"
    startBtn.addEventListener("click", () => {
      examIntro.style.display = "none";
      examContainer.style.display = "block";
      startTimer();
      loadQuestion(currentQuestionIndex);
    });
  
    // Hàm đếm ngược
    function startTimer() {
      countdown = setInterval(() => {
        remainingTime--;
        let minutes = Math.floor(remainingTime / 60);
        let seconds = remainingTime % 60;
        timerElement.textContent = `${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
        if (remainingTime <= 0) {
          clearInterval(countdown);
          finishExam();
        }
      }, 1000);
    }
  
    // Hàm load câu hỏi dựa trên index trong mảng examQuestions
    function loadQuestion(index) {
      // Nếu hết câu hỏi, hiển thị nút "Hoàn thành bài thi"
      if (index >= examQuestions.length) {
        showCompleteButton();
        return;
      }
      attemptsCurrentQuestion = 0;  // Reset số lần sai cho câu hiện tại
  
      const q = examQuestions[index];
      let html = `<div class="question" data-question-id="${q.id}">
                    <p class="question-text">Câu ${index + 1}: ${q.question}</p>`;
      if (q.question_type === "MCQ") {
        // Nếu là trắc nghiệm: parse choices từ JSON (nếu là chuỗi)
        let choices = typeof q.choices === "string" ? JSON.parse(q.choices) : q.choices;
        html += `<ul class="choices">`;
        for (const key in choices) {
          html += `<li>
                     <label>
                       <input type="radio" name="question${q.id}" value="${key}"> ${key}. ${choices[key]}
                     </label>
                   </li>`;
        }
        html += `</ul>`;
      } else if (q.question_type === "essay") {
        // Nếu là tự luận: hiển thị ô input
        html += `<input type="text" name="question${q.id}" placeholder="Nhập câu trả lời của bạn">`;
      }
      html += `</div>`;
      questionContainer.innerHTML = html;
    }
  
    // Xử lý nút "Nộp câu hỏi" cho câu hỏi hiện tại
    submitBtn.addEventListener("click", () => {
      const q = examQuestions[currentQuestionIndex];
      let userAnswer;
      if (q.question_type === "MCQ") {
        userAnswer = document.querySelector(`input[name="question${q.id}"]:checked`);
        if (!userAnswer) {
          alert("Vui lòng chọn đáp án.");
          return;
        }
        userAnswer = userAnswer.value;
      } else if (q.question_type === "essay") {
        userAnswer = document.querySelector(`input[name="question${q.id}"]`).value.trim();
        if (!userAnswer) {
          alert("Vui lòng nhập câu trả lời của bạn.");
          return;
        }
      }
      
      // So sánh đáp án
      if (userAnswer === q.answer) {
        score += 10;  // Ví dụ: mỗi câu đúng cộng 10 điểm
        scoreElement.textContent = "Điểm: " + score;
        currentQuestionIndex++;
        loadQuestion(currentQuestionIndex);
      } else {
        attemptsCurrentQuestion++;
        alert("Đáp án sai. Vui lòng thử lại.");
        if (attemptsCurrentQuestion >= 3) {
          alert("Bạn đã sai quá 3 lần ở câu này. Bài thi kết thúc!");
          finishExam();
        }
      }
    });
  
    // Hiển thị nút "Hoàn thành bài thi"
    function showCompleteButton() {
      completeBtn.style.display = "block";
    }
  
    // Xử lý khi bấm nút "Hoàn thành bài thi"
    completeBtn.addEventListener("click", finishExam);
  
    // Hàm kết thúc bài thi
    function finishExam() {
      clearInterval(countdown);
      // Chuyển hướng sang trang kết quả, truyền điểm, môn học và lớp qua URL
      window.location.href = `/result?score=${score}&subject=${examSubject}&grade=${examGrade}`;
    }
  });
  
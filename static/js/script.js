// Lắng nghe sự kiện 'submit' từ form đăng nhập
document.getElementById('loginForm').addEventListener('submit', function(event) {
  event.preventDefault(); // Ngăn hành động gửi form mặc định

  // Lấy giá trị nhập từ các input
  const usernameInput = document.getElementById('username');
  const passwordInput = document.getElementById('password');
  const username = usernameInput.value.trim();
  const password = passwordInput.value;
  const errorMessage = document.getElementById('error-message');
  const loginButton = document.getElementById('loginButton');

  // Xóa thông báo lỗi nếu có
  errorMessage.style.display = 'none';
  usernameInput.classList.remove('shake');
  passwordInput.classList.remove('shake');

  // Kiểm tra nếu input trống
  if (username === "" && password === "") {
    errorMessage.textContent = "Bạn chưa đăng nhập";
    errorMessage.style.display = "block";
    usernameInput.classList.add('shake');
    passwordInput.classList.add('shake');
    return;
  } else if (!username || !password) {
    errorMessage.textContent = "Vui lòng điền đầy đủ thông tin.";
    errorMessage.style.display = "block";
    usernameInput.classList.add('shake');
    passwordInput.classList.add('shake');
    return;
  }

  // Hiển thị trạng thái đang xử lý (spinner)
  loginButton.disabled = true;
  loginButton.innerHTML = 'Đang đăng nhập<span class="spinner"></span>';

  // Tạo URLSearchParams để đóng gói dữ liệu
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  // Gửi dữ liệu tới backend qua Fetch API đến route /login
  fetch('/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData.toString()
  })
    .then(response => response.json())
    .then(data => {
        console.log('Response from server:', data); // Debug kết quả từ server
        // Nếu server trả về "success", chuyển hướng người dùng sang trang exam
        if (data.status === 'success') {
            window.location.href = '/choose_exam';
        } else {
            // Nếu không, hiển thị thông báo lỗi từ backend
            errorMessage.style.display = 'block';
            errorMessage.textContent = data.message;
            // Reset lại button đăng nhập
            loginButton.disabled = false;
            loginButton.innerHTML = 'Đăng nhập';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        errorMessage.style.display = 'block';
        errorMessage.textContent = 'Có lỗi xảy ra. Vui lòng thử lại sau.';
        // Reset lại button đăng nhập
        loginButton.disabled = false;
        loginButton.innerHTML = 'Đăng nhập';
    });
});

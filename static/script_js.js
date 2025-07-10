// MPA版本的JavaScript - 移除了頁面切換功能

// FAQ展開/摺疊功能
function toggleFaq(element) {
    const answer = element.nextElementSibling;
    answer.classList.toggle('show');
    
    // 添加動畫效果
    if (answer.classList.contains('show')) {
        answer.style.display = 'block';
    } else {
        answer.style.display = 'none';
    }
}

// 當頁面載入完成後執行
document.addEventListener('DOMContentLoaded', function() {
    
    // 表單提交處理
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('感謝您的訊息！我們會盡快回覆您。');
            this.reset();
        });
    }

    // 課程報名按鈕處理
    const courseButtons = document.querySelectorAll('.course-signup-btn');
    courseButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('感謝您的報名！我們會盡快與您聯繫確認課程時間。');
        });
    });

    // 平滑滾動到頂部
    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        // 只對內部錨點連結添加平滑滾動
        if (link.getAttribute('href').startsWith('#')) {
            link.addEventListener('click', function() {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    });

    // 處理頁面內錨點滾動
    const hash = window.location.hash;
    if (hash) {
        setTimeout(() => {
            const target = document.querySelector(hash);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        }, 100);
    }
});

// 平滑進入動畫
function animateOnScroll() {
    const cards = document.querySelectorAll('.article-card, .course-card');
    
    cards.forEach(card => {
        const cardTop = card.getBoundingClientRect().top;
        const cardVisible = 150;
        
        if (cardTop < window.innerHeight - cardVisible) {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }
    });
}

// 滾動事件監聽
window.addEventListener('scroll', animateOnScroll);

// 初始化動畫
document.addEventListener('DOMContentLoaded', function() {
    // 設置初始狀態
    const cards = document.querySelectorAll('.article-card, .course-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
    
    // 觸發動畫
    setTimeout(animateOnScroll, 100);
});
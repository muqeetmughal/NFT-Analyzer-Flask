let menuHamburg = document.querySelectorAll('.menu-icon');
let chevronIcon = document.querySelectorAll('.chev-icon');
let backdropNav = document.querySelector('.backdrop-sidebar');
let sidebarNav = document.querySelector('.side-bar-wrapper');
let currentYear = document.querySelector('#currentyear');
// go to the section
const scrollTo_Section = (sec_id) => {
    let element = document.getElementById(sec_id);
    const yOffset = -100;
    if (element) {
        const y =
            element.getBoundingClientRect().top + window.pageYOffset + yOffset;
        window.scrollTo({ top: y, behavior: "smooth" });
    }
};

let sidebar = false;
const setSideBar = (openClose) => {
    sidebar = openClose;
    if (sidebar === true) {
        menuHamburg[0].classList.remove("show");
        menuHamburg[1].classList.add("show");
        chevronIcon[0].classList.remove("show");
        chevronIcon[1].classList.add("show");
        backdropNav.classList.add("show");
        sidebarNav.classList.add("opened-sidebar");
    } else {
        menuHamburg[1].classList.remove("show");
        menuHamburg[0].classList.add("show");
        chevronIcon[1].classList.remove("show");
        chevronIcon[0].classList.add("show");
        backdropNav.classList.remove("show");
        sidebarNav.classList.remove("opened-sidebar");
    }
};

currentYear.innerHTML = new Date().getFullYear();

window.onscroll = function() {
    var pageOffset = document.documentElement.scrollTop || document.body.scrollTop;
    let btn = document.getElementById('scrollToTop');
    if (btn) {
        if (pageOffset > 450) {
            btn.classList.add('show-top')
        } else {
            btn.classList.remove('show-top')
        }
    }
}

let closeNav = document.querySelectorAll(".handleNavOpenClose");
let goOnThePageTOp = document.querySelectorAll(".goOnThePageTOp");

closeNav.forEach((v, i) => {
    v.addEventListener("click", function(e) {
        console.log(e.target.dataset.nav)
        let val = e.target.dataset.nav;
        if (val === "open") {
            setSideBar(true)
        } else {
            setSideBar(false)
        }
    });
});


const goToTop = () => {
    window.scrollTo({
        top: 0,
        behavior: "smooth"
    })
};

goOnThePageTOp.forEach((v, i) => {
    v.addEventListener("click", function(e) {
        goToTop()
    });
});
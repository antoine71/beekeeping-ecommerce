const navItems = document.querySelector("#nav__items");
const openNavBtn = document.querySelector("#open__nav-btn");
const closeNavBtn = document.querySelector("#close__nav-btn");

// open close nav toggler

const openMenu = () => {
  navItems.style.display = "flex";
  openNavBtn.style.display = "none";
  closeNavBtn.style.display = "flex";
};

const closeMenu = () => {
  navItems.style.display = "none";
  openNavBtn.style.display = "flex";
  closeNavBtn.style.display = "none";
};

openNavBtn.addEventListener("click", openMenu);
closeNavBtn.addEventListener("click", closeMenu);

// close nav when a menu item is clocked

if (window.innerWidth < 1024) {
  document.querySelectorAll("#nav__items li a").forEach((navItem) => {
    navItem.addEventListener("click", closeMenu);
  });
}

// open close lang toggler

const langItems = document.querySelector("#lang__items");
const openLangBtn = document.querySelector("#open__lang-btn");
const closeLangBtn = document.querySelector("#close__lang-btn");

const openLangMenu = () => {
  langItems.style.display = "flex";
  openLangBtn.style.display = "none";
  closeLangBtn.style.display = "flex";
};

const closeLangMenu = () => {
  langItems.style.display = "none";
  openLangBtn.style.display = "flex";
  closeLangBtn.style.display = "none";
};

openLangBtn.addEventListener("click", openLangMenu);
closeLangBtn.addEventListener("click", closeLangMenu);

// close nav when a menu item is clocked

if (window.innerWidth < 1024) {
  document.querySelectorAll("#nav__items li a").forEach((langItem) => {
    langItem.addEventListener("click", closeLangMenu);
  });
}

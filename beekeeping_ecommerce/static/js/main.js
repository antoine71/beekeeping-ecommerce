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


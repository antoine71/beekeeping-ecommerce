const btnSocialsElt = document.querySelector("#btn-socials");
const divSocialsElt = document.querySelector("#div-socials");

btnSocialsElt.addEventListener("click", () => {
  divSocialsElt.style.display == "block"
    ? (divSocialsElt.style.display = "none")
    : (divSocialsElt.style.display = "block");
});

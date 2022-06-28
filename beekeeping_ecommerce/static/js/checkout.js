const billingAddressForm = document.querySelector("#hideable-shipping-form");
const formToggler = document.querySelector("#id_same_billing_address");

console.log(billingAddressForm)
console.log(formToggler)

const toggleForm = () => {
  formToggler.checked
  ? (billingAddressForm.style.display = "none")
  : (billingAddressForm.style.display = "block");
}

document.addEventListener('DOMContentLoaded', toggleForm);

formToggler.addEventListener("change", toggleForm);


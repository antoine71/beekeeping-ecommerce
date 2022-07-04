const billingAddressForm = document.querySelector("#hideable-shipping-form");
const formToggler = document.querySelector("#id_same_billing_address");

// Billing address form toggler

const toggleForm = () => {
  formToggler.checked
  ? (billingAddressForm.style.display = "none")
  : (billingAddressForm.style.display = "block");
}

document.addEventListener('DOMContentLoaded', toggleForm);

formToggler.addEventListener("change", toggleForm);


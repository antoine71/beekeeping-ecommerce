const shippingCountryElt = document.getElementById("id_shipping_country");
const csrfElt = document.querySelector('input[name="csrfmiddlewaretoken"]');
// update prices on dom loading

document.addEventListener("DOMContentLoaded", updateAllPrices);

// update prices on shipping country change

shippingCountryElt.addEventListener("change", async () => {
  r = await updateCountry();
  if (r.ok) {
    updateAllPrices();
  }
});

async function updateCountry() {
  data = {
    shipping_country: shippingCountryElt.value,
  };
  const config = {
    method: "POST",
    headers: {
      "X-CSRFToken": csrfElt.value,
      Accept: "application/json",
      "Content-Type": "application/json; charset=utf-8",
    },
    body: JSON.stringify(data),
  };
  r = await fetch(SELECT_COUNTRY_URL, config);
  return r;
}


// function that update prices
function updatePriceElt(priceEltId, price) {
  const priceElt = document.getElementById(priceEltId);
  priceElt.textContent = price;
}

function updateAllPrices() {
  fetchAndAppendOrderPrices();
  for (product_slug of getProductsSlug()) {
    fetchAndAppendProductPrices(product_slug);
  }
}

// functions that update order price

async function fetchAndAppendOrderPrices() {
  const prices = await fetchOrderPrices();
  updatePriceElt("order-price-ex-vat", prices.order_price_ex_vat);
  updatePriceElt("order-price-vat", prices.order_vat_price);
  updatePriceElt("order-price-ex-delivery", prices.order_price_ex_delivery);
  updatePriceElt("vat-rate", prices.vat_rate);
}

async function fetchOrderPrices() {
  const response = await fetch(ORDER_PRICES_URL);
  prices = await response.json();
  return prices;
}

// functions that update product price

async function fetchAndAppendProductPrices(productSlug) {
  const prices = await fetchProductPrices(productSlug);
  updatePriceElt(`${productSlug}-price`, prices.product_price_incl_vat);
  updatePriceElt(`${productSlug}-total-price`, prices.order_product_price);
}

async function fetchProductPrices(productSlug) {
  url = `${PRODUCT_PRICES_URL}/${productSlug}`;
  const response = await fetch(url);
  prices = await response.json();
  return prices;
}

function getProductsSlug() {
  orderProductElts = document.getElementsByClassName("order_product");
  productsSlug = Array.from(orderProductElts).map((elt) => {
    return elt.id;
  });
  return productsSlug;
}


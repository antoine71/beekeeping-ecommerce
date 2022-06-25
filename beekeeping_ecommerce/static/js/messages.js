messages = document.querySelectorAll('ul.django-messages>li')

messages.forEach(messageElt => {
  console.log('top')
  button = messageElt.querySelector('button');
  button.addEventListener('click', () => {
    messageElt.style.display = "none"
  })
});
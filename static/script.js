const messages = [
"کاشت امروز، برداشت مطمئن فردا؛ با سروبان در کنار شما.",
"امنیت مالی کشاورزان، هدف ما؛ سروبان، همراه همیشگی شما.",
"سروبان؛ اعتبار شما برای کشت قراردادی و خرید تضمینی!",
"محصولات شما، تعهد ما. با سروبان، آینده‌ای روشن‌تر بسازید.",
"حمایت از کشاورزی پایدار؛ سروبان، پلی به سوی موفقیت.",
"راه‌حل‌های مالی هوشمند برای کشاورزان؛ سروبان، شریک مطمئن شما.",
"با سروبان، دغدغه مالی را کنار بگذارید و به زمین خود اعتماد کنید.",
"کشت را به ما بسپارید؛ با تسهیلات سروبان، آینده‌ای سبزتر رقم بزنید.",
];


$('.chat-button').on('click' , function(){
	$('.chat-button').css({"display": "none"});
	
	$('.chat-box').css({"visibility": "visible"});
	appendMessage("سلام من سروناز هستم دستیار فروش سروبان. چه  محصولی مدنظر دارید؟", false);
});

$('.chat-box .chat-box-header p').on('click' , function(){
	$('.chat-button').css({"display": "block"});
	$('.chat-box').css({"visibility": "hidden"});
})

$("#addExtra").on("click" , function(){
		
		$(".modal").toggleClass("show-modal");
})

$(".modal-close-button").on("click" , function(){
	$(".modal").toggleClass("show-modal");
})

var $waitingDots='<span class="jumping-dots"><div class="randomMessage" id="randomMessage">لطفا صبر کنید...</div><div class="dots"><span class="dot-1"></span> <span class="dot-2"></span> <span class="dot-3"></span></span>'
var $chatBoxBody = $('.chat-box-body');
var $chatBoxFooterInput = $('.chat-box-footer input');
var $sendButton = $('.chat-box-footer .send');

$sendButton.on('click', function() {
	var message = $chatBoxFooterInput.val().trim();
	if (message) {
		appendMessage(message, true); // User message
		$chatBoxFooterInput.val('');

		sendToBot(message);

	}
});

$chatBoxFooterInput.on('keypress', function(e) {
	if (e.key === 'Enter') {
		$sendButton.click();
	}
});
function sendToBot(message) {


//add waiting dots

	$chatBoxBody.append($waitingDots);
	rotateMessage();
	// Send the message to the server
	$.ajax({
		url: '/api/chat',
		type: 'POST',
		contentType: 'application/json',
		data: JSON.stringify(
			{"user_id": "6", 
			"text": message}
		),
		success: function(response) {
			if (response.reply) {
				appendMessage(response.reply, false);
				if (response.cards && Array.isArray(response.cards)) {
					response.cards.forEach(product => {
						const card = createProductCard(product);
						appendMessage(card, false); // Bot message
					});
				}
				
			} else {
				appendMessage("خطا در دریافت پاسخ از سرور.", false);
			}
			$chatBoxBody.find('.jumping-dots').remove();
		},
		error: function() {
			appendMessage("خطا در ارسال پیام به سرور.", false);
			$chatBoxBody.find('.jumping-dots').remove();
		}
	});

}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';

    // Product image
    if (product.image && product.image.length > 0) {
		const imageContainer = document.createElement('div');
		imageContainer.className = 'image-cont';

        const img = document.createElement('img');
        img.src = `${product.imagePath}/${product.image[0]}`;
        img.alt = product.name;
        img.className = 'product-image';
        imageContainer.appendChild(img);
        card.appendChild(imageContainer);
    }

    // Product name
    const name = document.createElement('h3');
    name.textContent = product.name;
    card.appendChild(name);

    // Product price and unit
    const price = document.createElement('p');
    price.textContent = `قیمت: ${product.price.price} تومان (${product.unit})`;
    card.appendChild(price);

    // Product count
    if (product.price.count) {
        const count = document.createElement('p');
        count.textContent = `مقدار: ${product.price.count} ${product.unit}`;
        card.appendChild(count);
    }

    // Product location
    if (product.location && product.location.ostan && product.location.shahrestan) {
        const location = document.createElement('p');
        location.textContent = `مکان: ${product.location.ostan.label}، ${product.location.shahrestan.label}`;
        card.appendChild(location);
    }

    // Product availability
    if (product.availability) {
        const availability = document.createElement('p');
        availability.textContent = `وضعیت: ${product.availability}`;
        card.appendChild(availability);
    }

    // Product description
    if (product.description) {
        const desc = document.createElement('p');
        desc.innerHTML = product.description;
        card.appendChild(desc);
    }

    // Product link
    if (product.link) {
        const link = document.createElement('a');
        link.href = product.link;
        link.textContent = 'مشاهده جزئیات';
        link.target = '_blank';
        card.appendChild(link);
    }

    return card;
}


function appendMessage(message, isUser) {
	//check if message is a DOM element (for product cards)
	if (message instanceof HTMLElement) {
		var $messageDiv = $('<div>').addClass('chat-box-body-receive');
		$messageDiv.append(message);
		$chatBoxBody.append($messageDiv);
		$chatBoxBody.scrollTop($chatBoxBody[0].scrollHeight);
		return;
	}
	var $messageDiv = $('<div>').addClass(isUser ? 'chat-box-body-send' : 'chat-box-body-receive');
	var $messageContent = $('<p>').html(message);
	var now = new Date();
	var timestamp = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
	var $timestamp = $('<span>').text(timestamp);

	$messageDiv.append($messageContent).append($timestamp);
	$chatBoxBody.append($messageDiv);
	// $chatBoxBody.scrollTop($chatBoxBody[0].scrollHeight);
}



function rotateMessage() {
  const msgEl = document.getElementById("randomMessage");
  const randomMsg = messages[Math.floor(Math.random() * messages.length)];
  msgEl.textContent = randomMsg;
}

// Initial message



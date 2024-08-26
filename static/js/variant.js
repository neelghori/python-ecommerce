const productColors = document.querySelectorAll(".diagonal-square");
const productImages = document.querySelectorAll(".left-column img");

productColors.forEach((color, index) => {
    color.addEventListener("click", () => {
        productImages.forEach((image) => {
            image.classList.remove("active");
        });
        productImages[index].classList.add("active");

        productColors.forEach((c) => {
            c.classList.remove("active");
        });
        color.classList.add("active");

        {% comment %} Make a POST request to url 'get-price' with the ID as 'data-label-id' of the image selected  {% endcomment %}
        fetch("{% url 'get-price' %}", {
            method: "POST",
            body: JSON.stringify({ var_id: productImages[index].getAttribute("data-label-id") }),
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then((response) => response.json())
        .then((data) => {
            document.getElementById("price").innerText = data.price;
        });
    });
});
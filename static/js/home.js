document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.hero-image-panel img');
    let currentIndex = 0;

    function updateImageClasses() {
        images.forEach((img, index) => {
            img.classList.remove('active-1', 'active-2', 'active-3', 'fading-out', 'fading-in');
            if (index === currentIndex) {
                img.classList.add('active-1');
            } else if (index === (currentIndex + 1) % images.length) {
                img.classList.add('active-2');
            } else if (index === (currentIndex + 2) % images.length) {
                img.classList.add('active-3');
            }
        });
    }

    function transitionImages() {
        const fadingOutImage = images[currentIndex];
        const fadingInImage = images[(currentIndex + 3) % images.length];
        
        fadingOutImage.classList.add('fading-out');
        fadingInImage.classList.add('fading-in');
        
        setTimeout(() => {
            currentIndex = (currentIndex + 1) % images.length;
            updateImageClasses();
            
            // Start fading in the new back image
            setTimeout(() => {
                fadingInImage.classList.remove('fading-in');
                fadingInImage.classList.add('active-3');
            }, 50);
        }, 950); // Slightly less than the transition duration for smooth change
    }

    // Initialize the first set of images
    updateImageClasses();

    // Change image every 5 seconds
    setInterval(transitionImages, 5000);

    // Initialize AOS
    AOS.init();

    // Improved animated number counters
    function animateValue(id, start, end, duration) {
        const obj = document.getElementById(id);
        const range = end - start;
        const minTimer = 50; // minimum time between updates in milliseconds
        let stepTime = Math.abs(Math.floor(duration / range));
        stepTime = Math.max(stepTime, minTimer); // ensure stepTime is at least minTimer
        const startTime = new Date().getTime();
        const endTime = startTime + duration;
        let timer;

        function run() {
            const now = new Date().getTime();
            const remaining = Math.max((endTime - now) / duration, 0);
            const value = Math.round(end - (remaining * range));
            obj.innerHTML = value.toLocaleString() + '+';
            if (value == end) {
                clearInterval(timer);
            }
        }

        timer = setInterval(run, stepTime);
        run();
    }

    // Trigger animations when the section comes into view
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            animateValue("customerCount", 0, 5000, 2000);
            animateValue("handlesSold", 0, 50000, 2000);
            animateValue("yearsCount", 0, 25, 2000);
            observer.unobserve(entries[0].target);
        }
    }, { threshold: 0.5 });

    observer.observe(document.querySelector('.metrics-section'));

    // Sales Graph
    const ctx = document.getElementById('salesGraph').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['2019', '2020', '2021', '2022', '2023'],
            datasets: [{
                label: 'Annual Sales',
                data: [12000, 19000, 15000, 25000, 30000],
                borderColor: '#90CAF9',
                backgroundColor: 'rgba(144, 202, 249, 0.2)',
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#13b0ee',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Annual Sales Growth',
                    color: '#ffffff',
                    font: {
                        size: 18,
                        weight: '600',
                        family: "'Poppins', sans-serif"
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff',
                        font: {
                            family: "'Poppins', sans-serif"
                        }
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#ffffff',
                        font: {
                            family: "'Poppins', sans-serif"
                        }
                    }
                }
            }
        }
    });
});

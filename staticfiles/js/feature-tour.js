document.addEventListener('DOMContentLoaded', function() {
    // Check if this is the first visit (but only for authenticated users)
    if (!localStorage.getItem('featureTourShown') && document.body.contains(document.querySelector('.navbar'))) {
        setTimeout(showFeatureTour, 1500);
        localStorage.setItem('featureTourShown', 'true');
    }

    // Add click handler for help button
    const helpBtn = document.getElementById('show-feature-tour');
    if (helpBtn) {
        helpBtn.addEventListener('click', showFeatureTour);
    }
});

function showFeatureTour() {
    // Create modal background
    const modalBg = document.createElement('div');
    modalBg.className = 'feature-tour-bg';
    document.body.appendChild(modalBg);

    // Create modal content
    const modalContent = document.createElement('div');
    modalContent.className = 'feature-tour-content';
    modalBg.appendChild(modalContent);

    // Create header
    const header = document.createElement('div');
    header.className = 'feature-tour-header';
    modalContent.appendChild(header);

    // Add logo/title
    const title = document.createElement('h2');
    title.innerHTML = '<i class="fas fa-chart-pie me-2"></i>Welcome to SmartSpend';
    header.appendChild(title);

    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'feature-tour-close';
    closeBtn.innerHTML = '<i class="fas fa-times"></i>';
    closeBtn.addEventListener('click', function() {
        document.body.removeChild(modalBg);
    });
    header.appendChild(closeBtn);

    // Create content
    const featureContent = document.createElement('div');
    featureContent.className = 'feature-tour-body';
    modalContent.appendChild(featureContent);

    // Add welcome message
    const welcome = document.createElement('p');
    welcome.className = 'feature-tour-welcome';
    welcome.innerText = 'Your all-in-one solution for managing finances, tracking expenses, and achieving your savings goals!';
    featureContent.appendChild(welcome);

    // Create features grid
    const grid = document.createElement('div');
    grid.className = 'feature-tour-grid';
    featureContent.appendChild(grid);

    // Define features
    const features = [
        {
            icon: 'fa-money-bill-wave',
            title: 'Expense Tracking',
            description: 'Track both fixed and daily expenses with detailed categorization and receipt uploads.'
        },
        {
            icon: 'fa-wallet',
            title: 'Income Management',
            description: 'Record and categorize all your income sources to get a complete financial picture.'
        },
        {
            icon: 'fa-chart-bar',
            title: 'Budget Planning',
            description: 'Set monthly budgets by category and track your spending with visual progress bars.'
        },
        {
            icon: 'fa-piggy-bank',
            title: 'Savings Goals',
            description: 'Create and track progress toward your savings targets with visual indicators.'
        },
        {
            icon: 'fa-sync',
            title: 'Recurring Expenses',
            description: 'Configure expenses that repeat at set intervals with flexible frequency options.'
        },
        {
            icon: 'fa-chart-line',
            title: 'Financial Reports',
            description: 'Visualize spending patterns and gain insights with interactive charts and graphs.'
        },
        {
            icon: 'fa-lightbulb',
            title: 'Smart Suggestions',
            description: 'Get personalized recommendations to help improve your financial habits.'
        },
        {
            icon: 'fa-mobile-alt',
            title: 'Responsive Design',
            description: 'Access your finances from any device with our mobile-friendly interface.'
        }
    ];

    // Add feature items to grid
    features.forEach(feature => {
        const featureItem = document.createElement('div');
        featureItem.className = 'feature-tour-item';

        const iconDiv = document.createElement('div');
        iconDiv.className = 'feature-tour-icon';
        iconDiv.innerHTML = `<i class="fas ${feature.icon}"></i>`;
        featureItem.appendChild(iconDiv);

        const featureTitle = document.createElement('h3');
        featureTitle.innerText = feature.title;
        featureItem.appendChild(featureTitle);

        const featureDescription = document.createElement('p');
        featureDescription.innerText = feature.description;
        featureItem.appendChild(featureDescription);

        grid.appendChild(featureItem);
    });

    // Create footer
    const footer = document.createElement('div');
    footer.className = 'feature-tour-footer';
    modalContent.appendChild(footer);

    // Add get started button
    const startBtn = document.createElement('button');
    startBtn.className = 'btn btn-primary';
    startBtn.innerHTML = '<i class="fas fa-rocket me-2"></i>Get Started';
    startBtn.addEventListener('click', function() {
        document.body.removeChild(modalBg);
    });
    footer.appendChild(startBtn);

    // Check if dark mode is enabled and apply appropriate class
    if (document.body.getAttribute('data-bs-theme') === 'dark') {
        modalContent.classList.add('dark-mode');
    }

    // Animation effect
    setTimeout(() => {
        modalBg.classList.add('active');
        modalContent.classList.add('active');
    }, 10);
}
let riskChart = null;
let trendChart = null;
let analyticsChart = null;
let patientData = {};
let allAssessments = [];
let allAppointments = [];
let currentDate = new Date();
let currentAppointment = null;

// Initialize data from memory
function initializeData() {
    // Sample patient assessments for demonstration
    allAssessments = [
        {
            id: Date.now() - 10000,
            date: new Date().toLocaleDateString(),
            patientInfo: {
                name: "John Smith",
                contact: "555-0123",
                age: 45,
                gender: "Male",
                height: 175,
                weight: 85,
                bmi: 27.8
            },
            healthData: {
                systolic_bp: 140,
                diastolic_bp: 90,
                cholesterol: 220,
                glucose: 110,
                postprandial_glucose: 160,
                hba1c: 6.2,
                family_history: "1",
                exercise_hours: 2,
                serum_creatinine: 1.2,
                gfr: 85,
                urine_albumin: 30,
                blood_urea_nitrogen: 18
            },
            results: {
                riskLevel: "Moderate Risk",
                probability: 45,
                prediction: "Moderate risk assessment",
                recommendations: ["Exercise regularly", "Monitor blood pressure"]
            }
        },
        {
            id: Date.now() - 20000,
            date: new Date(Date.now() - 86400000).toLocaleDateString(),
            patientInfo: {
                name: "Sarah Johnson",
                contact: "555-0456",
                age: 32,
                gender: "Female",
                height: 165,
                weight: 68,
                bmi: 25.0
            },
            healthData: {
                systolic_bp: 120,
                diastolic_bp: 80,
                cholesterol: 180,
                glucose: 95,
                postprandial_glucose: 120,
                hba1c: 5.4,
                family_history: "0",
                exercise_hours: 5,
                serum_creatinine: 0.8,
                gfr: 95,
                urine_albumin: 10,
                blood_urea_nitrogen: 12
            },
            results: {
                riskLevel: "Low Risk",
                probability: 25,
                prediction: "Low risk assessment",
                recommendations: ["Maintain healthy lifestyle", "Regular check-ups"]
            }
        },
        {
            id: Date.now() - 30000,
            date: new Date(Date.now() - 172800000).toLocaleDateString(),
            patientInfo: {
                name: "Michael Brown",
                contact: "555-0789",
                age: 58,
                gender: "Male",
                height: 180,
                weight: 95,
                bmi: 29.3
            },
            healthData: {
                systolic_bp: 160,
                diastolic_bp: 100,
                cholesterol: 280,
                glucose: 140,
                postprandial_glucose: 220,
                hba1c: 7.8,
                family_history: "1",
                exercise_hours: 0,
                serum_creatinine: 2.1,
                gfr: 35,
                urine_albumin: 150,
                blood_urea_nitrogen: 45
            },
            results: {
                riskLevel: "High Risk",
                probability: 75,
                prediction: "High risk assessment",
                recommendations: ["Consult doctor immediately", "Start medication", "Diet modification"]
            }
        }
    ];

    // Sample appointments for demonstration
    allAppointments = [
        {
            id: Date.now() - 5000,
            patientName: "John Smith",
            contact: "555-0123",
            date: new Date().toISOString().split('T')[0],
            time: "10:00",
            type: "follow-up",
            priority: "medium",
            notes: "Follow-up for blood pressure monitoring",
            status: "scheduled",
            createdAt: new Date().toISOString()
        },
        {
            id: Date.now() - 15000,
            patientName: "Sarah Johnson",
            contact: "555-0456",
            date: new Date(Date.now() + 86400000).toISOString().split('T')[0],
            time: "14:30",
            type: "consultation",
            priority: "low",
            notes: "Regular health checkup",
            status: "scheduled",
            createdAt: new Date().toISOString()
        },
        {
            id: Date.now() - 25000,
            patientName: "Michael Brown",
            contact: "555-0789",
            date: new Date(Date.now() + 172800000).toISOString().split('T')[0],
            time: "09:00",
            type: "emergency",
            priority: "high",
            notes: "Urgent consultation for diabetes management",
            status: "scheduled",
            createdAt: new Date().toISOString()
        }
    ];
}

// Enhanced Disease selection functionality
function initializeDiseaseSelection() {
    const diseaseSelect = document.getElementById('diseaseSelect');
    const diseaseInfoPanel = document.getElementById('diseaseInfoPanel');
    const diseaseInfoText = document.getElementById('diseaseInfoText');

    if (!diseaseSelect) return;

    // Disease information mapping
    const diseaseInfo = {
        'diabetes': {
            title: 'Diabetes Assessment',
            description: 'This assessment will focus on blood glucose levels, HbA1c, and metabolic markers to evaluate diabetes risk.',
            icon: 'fa-syringe',
            parameters: ['Fasting Glucose', 'Postprandial Glucose', 'HbA1c', 'BMI', 'Blood Pressure']
        },
        'kidney': {
            title: 'Chronic Kidney Disease Assessment',
            description: 'This assessment will focus on kidney function markers including creatinine, GFR, and urine albumin levels.',
            icon: 'fa-kidneys',
            parameters: ['Serum Creatinine', 'GFR', 'Blood Urea Nitrogen', 'Urine Albumin', 'Hemoglobin']
        },
        'all': {
            title: 'Comprehensive Assessment',
            description: 'Complete health assessment covering all parameters for comprehensive risk evaluation.',
            icon: 'fa-heartbeat',
            parameters: ['All Health Parameters']
        }
    };

    // Handle disease selection change
    diseaseSelect.addEventListener('change', function () {
        const selectedDisease = this.value;

        // Hide error message when user selects
        document.getElementById('diseaseSelectError').style.display = 'none';

        if (selectedDisease && selectedDisease !== '') {
            const info = diseaseInfo[selectedDisease];

            // Show info panel with animation
            diseaseInfoPanel.style.display = 'block';

            // Update info text with parameters
            const parametersHTML = info.parameters.map(param =>
                `<span style="display: inline-block; background: #dbeafe; color: #1e40af; padding: 4px 10px; border-radius: 15px; margin: 3px; font-size: 0.85rem;">${param}</span>`
            ).join('');

            diseaseInfoText.innerHTML = `
                <div style="margin-bottom: 10px;">
                    <strong><i class="fas ${info.icon}"></i> ${info.title}</strong>
                </div>
                <div style="color: #475569; margin-bottom: 10px; font-size: 0.9rem;">
                    ${info.description}
                </div>
                <div style="margin-top: 12px;">
                    <strong style="font-size: 0.9rem; display: block; margin-bottom: 8px;">Key Parameters:</strong>
                    ${parametersHTML}
                </div>
            `;

            // Show/hide form fields based on selection
            toggleFormFields(selectedDisease);

            // Highlight relevant sections based on selection
            highlightRelevantSections(selectedDisease);
        } else {
            // Hide info panel
            diseaseInfoPanel.style.display = 'none';

            // Show all fields when no disease selected
            showAllFormFields();
            removeHighlights();
        }
    });
}

// Toggle form fields based on disease selection
function toggleFormFields(disease) {
    // Field IDs mapping - exactly as they appear in your HTML
    const diabetesFields = [
        'glucose', 'postprandial_glucose', 'hba1c'
    ];

    const kidneyFields = [
        'serum_creatinine', 'gfr', 'blood_urea_nitrogen',
        'urine_albumin', 'serum_potassium', 'hemoglobin'
    ];

    const commonFields = ['systolic_bp', 'diastolic_bp', 'cholesterol', 'family_history', 'exercise_hours'];

    // Get all unique fields
    const allFields = [...new Set([...diabetesFields, ...kidneyFields, ...commonFields])];

    allFields.forEach(fieldId => {
        const input = document.getElementById(fieldId);
        if (!input) {
            console.warn(`Field not found: ${fieldId}`);
            return;
        }

        const fieldGroup = input.closest('.form-group');
        if (!fieldGroup) {
            console.warn(`Form group not found for: ${fieldId}`);
            return;
        }

        const isCommon = commonFields.includes(fieldId);
        const isDiabetesField = diabetesFields.includes(fieldId);
        const isKidneyField = kidneyFields.includes(fieldId);

        if (disease === 'diabetes') {
            // Show diabetes and common fields, hide kidney-specific fields
            if (isDiabetesField || isCommon) {
                fieldGroup.style.display = 'block';
                // Make diabetes-specific required fields required
                if (isDiabetesField) {
                    input.setAttribute('required', 'required');
                }
            } else {
                fieldGroup.style.display = 'none';
                // Remove required attribute from hidden fields
                input.removeAttribute('required');
                input.value = ''; // Clear value when hiding
            }
        } else if (disease === 'kidney') {
            // Show kidney and common fields, hide diabetes-specific fields
            if (isKidneyField || isCommon) {
                fieldGroup.style.display = 'block';
                // Make kidney-specific required fields required
                if (isKidneyField) {
                    input.setAttribute('required', 'required');
                }
            } else {
                fieldGroup.style.display = 'none';
                // Remove required attribute from hidden fields
                input.removeAttribute('required');
                input.value = ''; // Clear value when hiding
            }
        } else if (disease === 'all') {
            // Show all fields
            fieldGroup.style.display = 'block';
            // Set required for key fields
            if (['systolic_bp', 'diastolic_bp', 'cholesterol', 'glucose', 'family_history',
                'serum_creatinine', 'gfr', 'blood_urea_nitrogen'].includes(fieldId)) {
                input.setAttribute('required', 'required');
            } else {
                input.removeAttribute('required');
            }
        }
    });

    // Also hide/show the section headers
    toggleSectionHeaders(disease);
}

// Toggle section headers based on disease selection
function toggleSectionHeaders(disease) {
    const sections = document.querySelectorAll('h3[style*="border-bottom"]');

    sections.forEach(section => {
        const sectionText = section.textContent.toLowerCase();

        if (disease === 'diabetes') {
            if (sectionText.includes('kidney')) {
                section.style.display = 'none';
            } else {
                section.style.display = 'block';
            }
        } else if (disease === 'kidney') {
            if (sectionText.includes('diabetes')) {
                section.style.display = 'none';
            } else {
                section.style.display = 'block';
            }
        } else {
            section.style.display = 'block';
        }
    });
}

// Show all form fields (when no specific disease is selected)
function showAllFormFields() {
    const allFieldIds = [
        'glucose', 'postprandial_glucose', 'hba1c',
        'systolic_bp', 'diastolic_bp', 'cholesterol', 'exercise_hours',
        'serum_creatinine', 'gfr', 'blood_urea_nitrogen',
        'urine_albumin', 'serum_potassium', 'hemoglobin', 'family_history'
    ];

    allFieldIds.forEach(fieldId => {
        const fieldGroup = document.getElementById(fieldId)?.closest('.form-group');
        if (fieldGroup) {
            fieldGroup.style.display = 'block';
        }

        // Reset required attributes to defaults
        const input = document.getElementById(fieldId);
        if (input && ['systolic_bp', 'diastolic_bp', 'cholesterol', 'glucose', 'family_history'].includes(fieldId)) {
            input.setAttribute('required', 'required');
        } else if (input) {
            input.removeAttribute('required');
        }
    });

    // Show all section headers
    const sections = document.querySelectorAll('h3[style*="border-bottom"]');
    sections.forEach(section => {
        section.style.display = 'block';
    });
}

// Highlight relevant form sections based on disease selection
function highlightRelevantSections(disease) {
    // Remove existing highlights
    removeHighlights();

    // Get all section headers
    const sections = document.querySelectorAll('h3[style*="border-bottom"]');

    sections.forEach(section => {
        const sectionText = section.textContent.toLowerCase();

        switch (disease) {
            case 'diabetes':
                if (sectionText.includes('diabetes') || sectionText.includes('lifestyle')) {
                    section.style.backgroundColor = '#dbeafe';
                    section.style.padding = '10px';
                    section.style.borderRadius = '8px';
                    section.style.margin = '10px 0';
                }
                break;
            case 'kidney':
                if (sectionText.includes('kidney') || sectionText.includes('lifestyle')) {
                    section.style.backgroundColor = '#fee2e2';
                    section.style.padding = '10px';
                    section.style.borderRadius = '8px';
                    section.style.margin = '10px 0';
                }
                break;
            case 'all':
                // Highlight all sections for comprehensive assessment
                section.style.backgroundColor = '#f0f9ff';
                section.style.padding = '10px';
                section.style.borderRadius = '8px';
                section.style.margin = '10px 0';
                break;
        }
    });
}

// Remove section highlights
function removeHighlights() {
    const sections = document.querySelectorAll('h3[style*="border-bottom"]');
    sections.forEach(section => {
        section.style.backgroundColor = '';
        section.style.padding = '';
        section.style.borderRadius = '';
        section.style.margin = '';
        section.style.animation = '';
    });
}

// Enhanced validation that considers selected disease
function validateAssessmentForm() {
    const selectedDisease = document.getElementById('diseaseSelect').value;
    let isValid = true;

    // Common validations (always required for all diseases)
    const systolicBp = document.getElementById('systolic_bp').value;
    const diastolicBp = document.getElementById('diastolic_bp').value;
    const cholesterol = document.getElementById('cholesterol').value;
    const familyHistory = document.getElementById('family_history').value;

    if (!systolicBp || systolicBp < 0 || systolicBp > 250) {
        document.getElementById('systolicBpError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('systolicBpError').style.display = 'none';
    }

    if (!diastolicBp || diastolicBp < 0 || diastolicBp > 250) {
        document.getElementById('diastolicBpError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('diastolicBpError').style.display = 'none';
    }

    if (!cholesterol || cholesterol < 0 || cholesterol > 400) {
        document.getElementById('cholesterolError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('cholesterolError').style.display = 'none';
    }

    if (!familyHistory) {
        document.getElementById('familyHistoryError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('familyHistoryError').style.display = 'none';
    }

    // Disease-specific validations
    if (selectedDisease === 'diabetes' || selectedDisease === 'all') {
        const glucose = document.getElementById('glucose').value;
        if (!glucose || glucose < 0 || glucose > 300) {
            document.getElementById('glucoseError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('glucoseError').style.display = 'none';
        }

        // Optional diabetes fields - only validate if they exist and are visible
        const postprandialGlucose = document.getElementById('postprandial_glucose');
        if (postprandialGlucose && postprandialGlucose.style.display !== 'none' && postprandialGlucose.value) {
            if (postprandialGlucose.value < 0 || postprandialGlucose.value > 500) {
                document.getElementById('postprandialGlucoseError').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('postprandialGlucoseError').style.display = 'none';
            }
        }

        const hba1c = document.getElementById('hba1c');
        if (hba1c && hba1c.style.display !== 'none' && hba1c.value) {
            if (hba1c.value < 0 || hba1c.value > 20) {
                document.getElementById('hba1cError').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('hba1cError').style.display = 'none';
            }
        }
        // Insulin Level validation
        const insulinLevel = document.getElementById('insulinLevel');
        if (insulinLevel && insulinLevel.style.display !== 'none' && insulinLevel.value) {
            if (insulinLevel.value < 0 || insulinLevel.value > 100) {
                document.getElementById('insulinLevelError').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('insulinLevelError').style.display = 'none';
            }
        }

        // C-Peptide Level validation
        const cPeptide = document.getElementById('cPeptide');
        if (cPeptide && cPeptide.style.display !== 'none' && cPeptide.value) {
            if (cPeptide.value < 0 || cPeptide.value > 10) {
                document.getElementById('cPeptideError').style.display = 'block';
                isValid = false;
            } else {
                document.getElementById('cPeptideError').style.display = 'none';
            }
        }
    }

    if (selectedDisease === 'kidney' || selectedDisease === 'all') {
        const creatinine = document.getElementById('serum_creatinine').value;
        if (!creatinine || creatinine < 0 || creatinine > 15) {
            document.getElementById('serumCreatinineError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('serumCreatinineError').style.display = 'none';
        }

        const gfr = document.getElementById('gfr').value;
        if (!gfr || gfr < 0 || gfr > 200) {
            document.getElementById('gfrError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('gfrError').style.display = 'none';
        }

        const bun = document.getElementById('blood_urea_nitrogen').value;
        if (!bun || bun < 0 || bun > 200) {
            document.getElementById('bunError').style.display = 'block';
            isValid = false;
        } else {
            document.getElementById('bunError').style.display = 'none';
        }
    }

    return isValid;
}

// Validate disease selection in the form
function validateDiseaseSelection() {
    const diseaseSelect = document.getElementById('diseaseSelect');
    const errorMessage = document.getElementById('diseaseSelectError');

    if (!diseaseSelect.value || diseaseSelect.value === '') {
        errorMessage.style.display = 'block';
        diseaseSelect.scrollIntoView({ behavior: 'smooth', block: 'center' });
        return false;
    }

    errorMessage.style.display = 'none';
    return true;
}

// Tab navigation functionality
document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', function () {
        // Update active tab
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');

        // Show corresponding section
        const targetId = this.getAttribute('data-target');
        document.getElementById('patientAssessmentContainer').style.display = targetId === 'patientTab' ? 'block' : 'none';
        document.getElementById('doctorTab').classList.toggle('hidden', targetId !== 'doctorTab');

        // If doctor dashboard is selected, update it
        if (targetId === 'doctorTab') {
            updateDoctorDashboard();
        }
    });
});

// Sidebar navigation functionality
document.querySelectorAll('.sidebar-nav-item').forEach(item => {
    item.addEventListener('click', function () {
        // Update active sidebar item
        document.querySelectorAll('.sidebar-nav-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');

        // Show corresponding view
        const section = this.getAttribute('data-section');
        document.getElementById('dashboardView').style.display = section === 'dashboard' ? 'block' : 'none';
        document.getElementById('patientsView').style.display = section === 'patients' ? 'block' : 'none';
        document.getElementById('scheduleView').style.display = section === 'schedule' ? 'block' : 'none';
        document.getElementById('analyticsView').style.display = section === 'analytics' ? 'block' : 'none';

        // Update view based on section
        if (section === 'patients') {
            populatePatientsTable();
        } else if (section === 'schedule') {
            initializeCalendar();
            populateAppointmentsList();
        } else if (section === 'analytics') {
            updateAnalytics();
        }
    });
});

// Add back button functionality to sidebar
function addBackButtonToSidebar() {
    const sidebarNav = document.querySelector('.sidebar-nav');

    // Check if back button already exists
    if (!document.getElementById('sidebarBackButton')) {
        const backButton = document.createElement('div');
        backButton.id = 'sidebarBackButton';
        backButton.className = 'sidebar-nav-item back-button';
        backButton.innerHTML = `
            <i class="fas fa-arrow-left"></i>
            <span>Back</span>
        `;

        backButton.addEventListener('click', function () {
            // Navigate back to patient assessment tab
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelector('[data-target="patientTab"]').classList.add('active');

            document.getElementById('patientAssessmentContainer').style.display = 'block';
            document.getElementById('doctorTab').classList.add('hidden');

            // Reset sidebar active state
            document.querySelectorAll('.sidebar-nav-item').forEach(i => i.classList.remove('active'));
        });

        // Add the back button to the bottom of the sidebar navigation
        sidebarNav.appendChild(backButton);
    }
}

// Schedule tab navigation
document.querySelectorAll('.schedule-tab').forEach(tab => {
    tab.addEventListener('click', function () {
        document.querySelectorAll('.schedule-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');

        const view = this.getAttribute('data-schedule-view');
        document.getElementById('calendarView').style.display = view === 'calendar' ? 'block' : 'none';
        document.getElementById('appointmentsView').style.display = view === 'appointments' ? 'block' : 'none';
        document.getElementById('addAppointmentView').style.display = view === 'add-appointment' ? 'block' : 'none';

        if (view === 'appointments') {
            populateAppointmentsList();
        } else if (view === 'calendar') {
            renderCalendar();
        }
    });
});

// Calendar functionality
function initializeCalendar() {
    currentDate = new Date();
    renderCalendar();

    document.getElementById('prevMonth').addEventListener('click', function () {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', function () {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    document.getElementById('todayBtn').addEventListener('click', function () {
        currentDate = new Date();
        renderCalendar();
    });

    document.getElementById('newAppointmentBtn').addEventListener('click', function () {
        document.querySelectorAll('.schedule-tab').forEach(t => t.classList.remove('active'));
        document.querySelector('[data-schedule-view="add-appointment"]').classList.add('active');
        document.getElementById('calendarView').style.display = 'none';
        document.getElementById('addAppointmentView').style.display = 'block';
    });
}

function renderCalendar() {
    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];
    const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

    document.getElementById('currentMonth').textContent = `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;

    const grid = document.getElementById('calendarGrid');
    grid.innerHTML = '';

    // Add day headers
    dayNames.forEach(day => {
        const dayHeader = document.createElement('div');
        dayHeader.className = 'calendar-day-header';
        dayHeader.textContent = day;
        grid.appendChild(dayHeader);
    });

    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const today = new Date();

    for (let i = 0; i < 42; i++) {
        const cellDate = new Date(startDate);
        cellDate.setDate(startDate.getDate() + i);

        const dayCell = document.createElement('div');
        dayCell.className = 'calendar-day';

        if (cellDate.getMonth() !== currentDate.getMonth()) {
            dayCell.classList.add('other-month');
        }

        if (cellDate.toDateString() === today.toDateString()) {
            dayCell.classList.add('today');
        }

        const dayNumber = document.createElement('div');
        dayNumber.className = 'calendar-day-number';
        dayNumber.textContent = cellDate.getDate();
        dayCell.appendChild(dayNumber);

        // Add appointments for this day
        const dayAppointments = getAppointmentsForDate(cellDate);
        dayAppointments.forEach(appointment => {
            const appointmentElement = document.createElement('div');
            appointmentElement.className = `calendar-appointment ${appointment.priority}-priority`;
            appointmentElement.textContent = `${appointment.time} ${appointment.patientName}`;
            appointmentElement.addEventListener('click', function (e) {
                e.stopPropagation();
                showAppointmentDetails(appointment);
            });
            dayCell.appendChild(appointmentElement);
        });

        // Add click handler for day
        dayCell.addEventListener('click', function () {
            const dateStr = cellDate.toISOString().split('T')[0];
            document.getElementById('appointmentDate').value = dateStr;
            document.querySelectorAll('.schedule-tab').forEach(t => t.classList.remove('active'));
            document.querySelector('[data-schedule-view="add-appointment"]').classList.add('active');
            document.getElementById('calendarView').style.display = 'none';
            document.getElementById('addAppointmentView').style.display = 'block';
        });

        grid.appendChild(dayCell);
    }
}

function getAppointmentsForDate(date) {
    const dateStr = date.toISOString().split('T')[0];
    return allAppointments.filter(appointment => appointment.date === dateStr);
}

// Appointment form handling
document.getElementById('appointmentForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const appointmentData = {
        id: Date.now(),
        patientName: formData.get('patientName'),
        contact: formData.get('contact'),
        date: formData.get('date'),
        time: formData.get('time'),
        type: formData.get('type'),
        priority: formData.get('priority'),
        notes: formData.get('notes') || '',
        status: 'scheduled',
        createdAt: new Date().toISOString()
    };

    allAppointments.push(appointmentData);

    // Reset form
    this.reset();

    // Switch back to calendar view
    document.querySelectorAll('.schedule-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-schedule-view="calendar"]').classList.add('active');
    document.getElementById('addAppointmentView').style.display = 'none';
    document.getElementById('calendarView').style.display = 'block';

    // Re-render calendar
    renderCalendar();
    updateDoctorDashboard();

    alert('Appointment scheduled successfully!');
});

document.getElementById('cancelAppointment').addEventListener('click', function () {
    document.getElementById('appointmentForm').reset();
    document.querySelectorAll('.schedule-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-schedule-view="calendar"]').classList.add('active');
    document.getElementById('addAppointmentView').style.display = 'none';
    document.getElementById('calendarView').style.display = 'block';
});

// Populate appointments list
function populateAppointmentsList() {
    const appointmentsList = document.getElementById('appointmentsList');

    if (allAppointments.length === 0) {
        appointmentsList.innerHTML = '<div class="appointment-card">No appointments scheduled</div>';
        return;
    }

    appointmentsList.innerHTML = '';
    allAppointments.sort((a, b) => new Date(`${a.date} ${a.time}`) - new Date(`${b.date} ${b.time}`))
        .forEach(appointment => {
            const appointmentCard = document.createElement('div');
            appointmentCard.className = `appointment-card priority-${appointment.priority}`;

            appointmentCard.innerHTML = `
                        <div class="appointment-header">
                            <div class="appointment-title">${appointment.patientName}</div>
                            <div class="appointment-time">${formatTime(appointment.time)}</div>
                        </div>
                        <div class="appointment-details">
                            <div><i class="fas fa-calendar"></i> ${formatDate(appointment.date)}</div>
                            <div><i class="fas fa-phone"></i> ${appointment.contact}</div>
                            <div><i class="fas fa-stethoscope"></i> ${appointment.type}</div>
                            <div><i class="fas fa-flag"></i> ${appointment.priority} Priority</div>
                        </div>
                        ${appointment.notes ? `<div style="margin-top: 10px; color: var(--light-text);"><i class="fas fa-notes-medical"></i> ${appointment.notes}</div>` : ''}
                        <div class="appointment-actions">
                            <button class="btn-small btn-edit" onclick="editAppointment('${appointment.id}')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn-small btn-delete" onclick="deleteAppointment('${appointment.id}')">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                            <button class="btn-small btn-complete" onclick="completeAppointment('${appointment.id}')">
                                <i class="fas fa-check"></i> Complete
                            </button>
                        </div>
                    `;

            appointmentsList.appendChild(appointmentCard);
        });
}

function formatTime(time) {
    const [hours, minutes] = time.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showAppointmentDetails(appointment) {
    currentAppointment = appointment;
    document.getElementById('modalTitle').textContent = `Appointment - ${appointment.patientName}`;

    const modalBody = document.getElementById('modalBody');
    modalBody.innerHTML = `
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0;">
                    <div><strong>Patient:</strong> ${appointment.patientName}</div>
                    <div><strong>Contact:</strong> ${appointment.contact}</div>
                    <div><strong>Date:</strong> ${formatDate(appointment.date)}</div>
                    <div><strong>Time:</strong> ${formatTime(appointment.time)}</div>
                    <div><strong>Type:</strong> ${appointment.type}</div>
                    <div><strong>Priority:</strong> ${appointment.priority}</div>
                    <div><strong>Status:</strong> ${appointment.status}</div>
                </div>
                ${appointment.notes ? `<div><strong>Notes:</strong><br>${appointment.notes}</div>` : ''}
            `;

    document.getElementById('appointmentModal').style.display = 'block';
}

function editAppointment(id) {
    const appointment = allAppointments.find(a => a.id == id);
    if (!appointment) return;

    // Populate form with appointment data
    document.getElementById('appointmentPatientName').value = appointment.patientName;
    document.getElementById('appointmentContact').value = appointment.contact;
    document.getElementById('appointmentDate').value = appointment.date;
    document.getElementById('appointmentTime').value = appointment.time;
    document.getElementById('appointmentType').value = appointment.type;
    document.getElementById('appointmentPriority').value = appointment.priority;
    document.getElementById('appointmentNotes').value = appointment.notes;

    // Remove existing appointment
    deleteAppointment(id, false);

    // Switch to add appointment view
    document.querySelectorAll('.schedule-tab').forEach(t => t.classList.remove('active'));
    document.querySelector('[data-schedule-view="add-appointment"]').classList.add('active');
    document.getElementById('appointmentsView').style.display = 'none';
    document.getElementById('addAppointmentView').style.display = 'block';
}

function deleteAppointment(id, confirm = true) {
    if (confirm && !window.confirm('Are you sure you want to delete this appointment?')) return;

    allAppointments = allAppointments.filter(a => a.id != id);
    populateAppointmentsList();
    renderCalendar();
    updateDoctorDashboard();

    if (confirm) alert('Appointment deleted successfully!');
}

function completeAppointment(id) {
    const appointment = allAppointments.find(a => a.id == id);
    if (!appointment) return;

    appointment.status = 'completed';
    populateAppointmentsList();
    renderCalendar();
    updateDoctorDashboard();

    alert('Appointment marked as completed!');
}

// Modal functionality
document.getElementById('closeModal').addEventListener('click', function () {
    document.getElementById('appointmentModal').style.display = 'none';
});

document.getElementById('editAppointmentBtn').addEventListener('click', function () {
    if (currentAppointment) {
        editAppointment(currentAppointment.id);
        document.getElementById('appointmentModal').style.display = 'none';
    }
});

document.getElementById('deleteAppointmentBtn').addEventListener('click', function () {
    if (currentAppointment) {
        deleteAppointment(currentAppointment.id);
        document.getElementById('appointmentModal').style.display = 'none';
    }
});

document.getElementById('completeAppointmentBtn').addEventListener('click', function () {
    if (currentAppointment) {
        completeAppointment(currentAppointment.id);
        document.getElementById('appointmentModal').style.display = 'none';
    }
});

window.addEventListener('click', function (e) {
    if (e.target === document.getElementById('appointmentModal')) {
        document.getElementById('appointmentModal').style.display = 'none';
    }
});

// Handle patient registration form
document.getElementById('patientRegistrationForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Validate inputs
    if (!validateRegistrationForm()) {
        return;
    }

    // Store patient information
    patientData = {
        fullName: document.getElementById('fullName').value,
        contactNumber: document.getElementById('contactNumber').value,
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        height: document.getElementById('height').value,
        weight: document.getElementById('weight').value
    };

    // Update patient info display
    document.getElementById('patientNameDisplay').innerHTML += patientData.fullName;
    document.getElementById('patientContactDisplay').innerHTML += patientData.contactNumber;
    document.getElementById('patientAgeDisplay').innerHTML += patientData.age + ' years';
    document.getElementById('patientGenderDisplay').innerHTML += (patientData.gender === "1" ? "Male" : "Female");

    // Hide registration and show assessment
    document.getElementById('registrationSection').style.display = 'none';
    document.getElementById('assessmentSection').style.display = 'block';

    // Scroll to top
    window.scrollTo(0, 0);
});

// Validate registration form
function validateRegistrationForm() {
    let isValid = true;

    // Full Name validation
    const fullName = document.getElementById('fullName').value;
    if (!fullName || fullName.trim().length < 2) {
        document.getElementById('fullNameError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('fullNameError').style.display = 'none';
    }

    // Contact Number validation
    const contactNumber = document.getElementById('contactNumber').value;
    if (!contactNumber || contactNumber.length < 10) {
        document.getElementById('contactNumberError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('contactNumberError').style.display = 'none';
    }

    // Age validation
    const age = document.getElementById('age').value;
    if (!age || age < 1 || age > 120) {
        document.getElementById('ageError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('ageError').style.display = 'none';
    }

    // Gender validation
    const gender = document.getElementById('gender').value;
    if (!gender) {
        document.getElementById('genderError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('genderError').style.display = 'none';
    }

    // Height validation
    const height = document.getElementById('height').value;
    if (!height || height < 0 || height > 250) {
        document.getElementById('heightError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('heightError').style.display = 'none';
    }

    // Weight validation
    const weight = document.getElementById('weight').value;
    if (!weight || weight < 0 || weight > 300) {
        document.getElementById('weightError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('weightError').style.display = 'none';
    }

    return isValid;
}

// Back to registration button
document.getElementById('backToRegistration').addEventListener('click', function () {
    document.getElementById('assessmentSection').style.display = 'none';
    document.getElementById('registrationSection').style.display = 'block';
    window.scrollTo(0, 0);
});

// Back to assessment button
document.getElementById('backToAssessment').addEventListener('click', function () {
    document.getElementById('resultsSection').style.display = 'none';
    window.scrollTo(0, 0);
});

// New assessment button
document.getElementById('newAssessmentBtn').addEventListener('click', function () {
    // Reset forms
    document.getElementById('patientRegistrationForm').reset();
    document.getElementById('predictionForm').reset();
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('assessmentSection').style.display = 'none';
    document.getElementById('registrationSection').style.display = 'block';

    // Clear patient info display
    document.getElementById('patientNameDisplay').innerHTML = '<i class="fas fa-user"></i> ';
    document.getElementById('patientContactDisplay').innerHTML = '<i class="fas fa-phone"></i> ';
    document.getElementById('patientAgeDisplay').innerHTML = '<i class="fas fa-birthday-cake"></i> ';
    document.getElementById('patientGenderDisplay').innerHTML = '<i class="fas fa-venus-mars"></i> ';

    window.scrollTo(0, 0);
});

// Handle risk prediction form
document.getElementById('predictionForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    // Validate disease selection first
    if (!validateDiseaseSelection()) {
        return;
    }

    // Validate assessment form
    if (!validateAssessmentForm()) {
        return;
    }

    const submitBtn = document.querySelector('#predictionForm .predict-btn');
    const btnText = document.querySelector('#predictionForm .btn-text');
    const loading = document.querySelector('#predictionForm .loading');

    // Show loading state
    btnText.style.display = 'none';
    loading.style.display = 'inline';
    submitBtn.disabled = true;

    // Hide previous results
    document.getElementById('resultsSection').style.display = 'none';

    try {
        // Combine patient data with health assessment data
        const formData = new FormData(this);
        const healthData = Object.fromEntries(formData.entries());
        const completeData = { ...patientData, ...healthData };

        // Calculate BMI
        const heightInMeters = patientData.height / 100;
        const bmi = (patientData.weight / (heightInMeters * heightInMeters));
        completeData.bmi = bmi;

        // Add selected disease type to data
        completeData.selectedDisease = document.getElementById('diseaseSelect').value;

        // Simulate API call (in a real app, you would send this to your backend)
        console.log('Submitting data:', completeData);

        // Simulate delay for API call
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Generate mock results (replace with actual API response)
        const mockResults = generateMockResults(completeData);

        // Save assessment
        saveAssessment(completeData, mockResults);

        displayResults(mockResults);
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        loading.style.display = 'none';
        submitBtn.disabled = false;
    }
});

// Validate kidney function markers
function validateKidneyMarkers() {
    let isValid = true;

    // Serum Creatinine validation
    const creatinine = document.getElementById('serum_creatinine').value;
    if (!creatinine || creatinine < 0 || creatinine > 15) {
        document.getElementById('serumCreatinineError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('serumCreatinineError').style.display = 'none';
    }

    // GFR validation
    const gfr = document.getElementById('gfr').value;
    if (!gfr || gfr < 0 || gfr > 200) {
        document.getElementById('gfrError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('gfrError').style.display = 'none';
    }

    // Blood Urea Nitrogen validation
    const bun = document.getElementById('blood_urea_nitrogen').value;
    if (!bun || bun < 0 || bun > 200) {
        document.getElementById('bunError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('bunError').style.display = 'none';
    }

    // Urine albumin validation (optional)
    const urineAlbumin = document.getElementById('urine_albumin').value;
    if (urineAlbumin && (urineAlbumin < 0 || urineAlbumin > 5000)) {
        document.getElementById('urineAlbuminError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('urineAlbuminError').style.display = 'none';
    }

    // Serum potassium validation (optional)
    const serumPotassium = document.getElementById('serum_potassium').value;
    if (serumPotassium && (serumPotassium < 0 || serumPotassium > 10)) {
        document.getElementById('serumPotassiumError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('serumPotassiumError').style.display = 'none';
    }

    // Hemoglobin validation (optional)
    const hemoglobin = document.getElementById('hemoglobin').value;
    if (hemoglobin && (hemoglobin < 0 || hemoglobin > 25)) {
        document.getElementById('hemoglobinError').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('hemoglobinError').style.display = 'none';
    }

    return isValid;
}

// Save assessment
function saveAssessment(patientData, results) {
    const assessment = {
        id: Date.now(),
        date: new Date().toLocaleDateString(),
        patientInfo: {
            name: patientData.fullName,
            contact: patientData.contactNumber,
            age: patientData.age,
            gender: patientData.gender === "1" ? "Male" : "Female",
            height: patientData.height,
            weight: patientData.weight,
            bmi: patientData.bmi
        },
        healthData: {
            systolic_bp: patientData.systolic_bp,
            diastolic_bp: patientData.diastolic_bp,
            cholesterol: patientData.cholesterol,
            glucose: patientData.glucose,
            postprandial_glucose: patientData.postprandial_glucose || null,
            hba1c: patientData.hba1c || null,
            family_history: patientData.family_history,
            exercise_hours: patientData.exercise_hours || 0,
            serum_creatinine: patientData.serum_creatinine || null,
            gfr: patientData.gfr || null,
            urine_albumin: patientData.urine_albumin || null,
            blood_urea_nitrogen: patientData.blood_urea_nitrogen || null,
            serum_potassium: patientData.serum_potassium || null,
            hemoglobin: patientData.hemoglobin || null
        },
        selectedDisease: patientData.selectedDisease || 'all',
        results: {
            riskLevel: results.risk_level,
            probability: results.probability,
            prediction: results.prediction,
            recommendations: results.recommendations,
            kidneyRisk: results.kidney_risk,
            ckdStage: results.ckd_stage
        }
    };

    allAssessments.push(assessment);
}

// Calculate kidney risk
function calculateKidneyRisk(data) {
    let kidneyRiskScore = 0;
    let kidneyRiskFactors = [];

    const creatinine = parseFloat(data.serum_creatinine) || 1.0;
    const gfr = parseInt(data.gfr) || 90;
    const urineAlbumin = parseInt(data.urine_albumin) || 0;
    const bun = parseInt(data.blood_urea_nitrogen) || 15;

    // eGFR based risk
    if (gfr < 30) {
        kidneyRiskScore += 40;
        kidneyRiskFactors.push('Severely reduced kidney function (Stage 4-5 CKD)');
    } else if (gfr < 60) {
        kidneyRiskScore += 25;
        kidneyRiskFactors.push('Moderately reduced kidney function (Stage 3 CKD)');
    } else if (gfr < 90) {
        kidneyRiskScore += 10;
        kidneyRiskFactors.push('Mildly reduced kidney function');
    }

    // Creatinine risk
    if (creatinine > 1.3) {
        kidneyRiskScore += 15;
        kidneyRiskFactors.push('Elevated creatinine levels');
    }

    // Albuminuria risk
    if (urineAlbumin > 30) {
        kidneyRiskScore += 20;
        kidneyRiskFactors.push('Significant albuminuria');
    } else if (urineAlbumin > 10) {
        kidneyRiskScore += 10;
        kidneyRiskFactors.push('Mild albuminuria');
    }

    // BUN risk
    if (bun > 25) {
        kidneyRiskScore += 10;
        kidneyRiskFactors.push('Elevated BUN levels');
    }

    return {
        score: kidneyRiskScore,
        factors: kidneyRiskFactors,
        ckdStage: getCKDStage(gfr)
    };
}

function getCKDStage(gfr) {
    if (gfr >= 90) return 'Stage 1 (Normal)';
    if (gfr >= 60) return 'Stage 2 (Mild)';
    if (gfr >= 30) return 'Stage 3 (Moderate)';
    if (gfr >= 15) return 'Stage 4 (Severe)';
    return 'Stage 5 (Kidney Failure)';
}

// Get kidney-specific recommendations
function getKidneyRecommendations(kidneyRisk) {
    const recs = [];

    if (kidneyRisk.ckdStage !== 'Stage 1 (Normal)') {
        recs.push(`Consult nephrologist for ${kidneyRisk.ckdStage} chronic kidney disease`);
    }

    if (kidneyRisk.score > 20) {
        recs.push('Monitor kidney function with regular blood and urine tests');
        recs.push('Control blood pressure and diabetes strictly');
        recs.push('Consider dietary modifications (reduce sodium, potassium if needed)');
    }

    if (kidneyRisk.score > 40) {
        recs.push('Immediate nephrology referral required');
        recs.push('Discuss renal replacement therapy options');
        recs.push('Monitor fluid intake and electrolyte balance');
    }

    if (kidneyRisk.score > 0) {
        recs.push('Avoid nephrotoxic medications (NSAIDs, certain antibiotics)');
        recs.push('Maintain optimal hydration');
    }

    return recs;
}

// Generate mock results for demonstration
function generateMockResults(data) {
    let riskScore = 0;
    let riskFactors = [];

    // Calculate risk based on various factors
    const bmi = data.bmi;
    const age = parseInt(data.age);
    const systolic = parseInt(data.systolic_bp);
    const diastolic = parseInt(data.diastolic_bp);
    const cholesterol = parseInt(data.cholesterol);
    const glucose = parseInt(data.glucose);
    const postprandialGlucose = data.postprandial_glucose ? parseInt(data.postprandial_glucose) : null;
    const hba1c = data.hba1c ? parseFloat(data.hba1c) : null;
    const familyHistory = data.family_history === '1';
    const exercise = parseFloat(data.exercise_hours) || 0;
    const selectedDisease = data.selectedDisease || 'all';

    // BMI risk factor
    if (bmi >= 30) {
        riskScore += 25;
        riskFactors.push('High BMI (obesity)');
    } else if (bmi >= 25) {
        riskScore += 15;
        riskFactors.push('Overweight BMI');
    }

    // Age risk factor
    if (age >= 65) {
        riskScore += 20;
        riskFactors.push('Advanced age');
    } else if (age >= 45) {
        riskScore += 10;
        riskFactors.push('Middle age');
    }

    // Blood pressure risk factor
    if (systolic >= 140 || diastolic >= 90) {
        riskScore += 25;
        riskFactors.push('High blood pressure');
    } else if (systolic >= 130 || diastolic >= 80) {
        riskScore += 15;
        riskFactors.push('Elevated blood pressure');
    }

    // Cholesterol risk factor
    if (cholesterol >= 240) {
        riskScore += 20;
        riskFactors.push('High cholesterol');
    } else if (cholesterol >= 200) {
        riskScore += 10;
        riskFactors.push('Borderline high cholesterol');
    }

    // Glucose risk factor
    if (glucose >= 126) {
        riskScore += 30;
        riskFactors.push('Diabetes/Pre-diabetes (fasting glucose)');
    } else if (glucose >= 100) {
        riskScore += 15;
        riskFactors.push('Impaired fasting glucose');
    }

    // Postprandial glucose risk factor
    if (postprandialGlucose) {
        if (postprandialGlucose >= 200) {
            riskScore += 25;
            riskFactors.push('High postprandial glucose (diabetes range)');
        } else if (postprandialGlucose >= 140) {
            riskScore += 15;
            riskFactors.push('Elevated postprandial glucose (pre-diabetes)');
        }
    }

    // HbA1c risk factor
    if (hba1c) {
        if (hba1c >= 6.5) {
            riskScore += 30;
            riskFactors.push('High HbA1c (diabetes range)');
        } else if (hba1c >= 5.7) {
            riskScore += 20;
            riskFactors.push('Elevated HbA1c (pre-diabetes)');
        }
    }

    // Family history risk factor
    if (familyHistory) {
        riskScore += 15;
        riskFactors.push('Family history of chronic disease');
    }

    // Exercise protective factor
    if (exercise >= 5) {
        riskScore -= 10;
    } else if (exercise >= 2.5) {
        riskScore -= 5;
    } else if (exercise === 0) {
        riskScore += 10;
        riskFactors.push('Sedentary lifestyle');
    }

    // Add kidney risk assessment
    const kidneyRisk = calculateKidneyRisk(data);
    riskScore += kidneyRisk.score;
    riskFactors.push(...kidneyRisk.factors);

    // Adjust risk score based on selected disease
    if (selectedDisease === 'diabetes' && (glucose >= 100 || hba1c >= 5.7)) {
        riskScore += 10;
    } else if (selectedDisease === 'kidney' && kidneyRisk.score > 0) {
        riskScore += 10;
    }

    // Ensure score is within bounds
    riskScore = Math.max(0, Math.min(100, riskScore));

    let riskLevel, riskClass, prediction, recommendations;

    if (riskScore < 30) {
        riskLevel = 'Low Risk';
        riskClass = 'low-risk';
        prediction = `Based on the assessment, you have a low risk of developing chronic diseases. Your current health indicators are within healthy ranges. Continue maintaining your healthy lifestyle to keep your risk low.`;
        recommendations = [
            'Maintain a balanced diet rich in fruits, vegetables, and whole grains',
            'Continue regular physical activity (at least 150 minutes per week)',
            'Get regular health screenings as recommended by your doctor',
            'Maintain a healthy weight and BMI',
            'Limit alcohol consumption and avoid smoking',
            'Manage stress through healthy coping mechanisms'
        ];
    } else if (riskScore < 60) {
        riskLevel = 'Moderate Risk';
        riskClass = 'moderate-risk';
        prediction = `Your assessment indicates a moderate risk for chronic diseases. Some of your health indicators suggest areas for improvement. With lifestyle modifications, you can significantly reduce your risk.`;
        recommendations = [
            'Consult with your healthcare provider for personalized advice',
            'Focus on weight management if BMI is elevated',
            'Increase physical activity to at least 150 minutes per week',
            'Monitor blood pressure and cholesterol levels regularly',
            'Consider dietary modifications to improve metabolic health',
            'Implement stress reduction techniques',
            'Schedule more frequent health check-ups'
        ];
    } else {
        riskLevel = 'High Risk';
        riskClass = 'high-risk';
        prediction = `Your assessment indicates a high risk for chronic diseases. Multiple risk factors have been identified that require immediate attention. It's strongly recommended to consult with healthcare professionals for comprehensive evaluation and treatment.`;
        recommendations = [
            'Schedule an immediate appointment with your healthcare provider',
            'Discuss medication options if lifestyle changes are insufficient',
            'Work with a registered dietitian for meal planning',
            'Consider supervised exercise programs',
            'Monitor blood sugar, blood pressure, and cholesterol closely',
            'Join support groups or diabetes prevention programs',
            'Get regular screenings for complications',
            'Consider working with an endocrinologist or cardiologist'
        ];
    }

    // Add kidney-specific recommendations if kidney risk is present
    if (kidneyRisk.score > 0) {
        recommendations.push(...getKidneyRecommendations(kidneyRisk));
    }

    // Add disease-specific recommendations
    if (selectedDisease === 'diabetes') {
        recommendations.push('Focus on blood glucose monitoring and management');
        recommendations.push('Consider continuous glucose monitoring if needed');
    } else if (selectedDisease === 'kidney') {
        recommendations.push('Prioritize kidney health with adequate hydration');
        recommendations.push('Monitor protein intake based on kidney function');
    }

    return {
        risk_level: riskLevel,
        probability: riskScore,
        prediction: prediction,
        recommendations: recommendations,
        risk_class: riskClass,
        risk_factors: riskFactors,
        kidney_risk: kidneyRisk,
        ckd_stage: kidneyRisk.ckdStage,
        selected_disease: selectedDisease
    };
}

// Display results
function displayResults(results) {
    // Update risk indicator
    const riskIndicator = document.getElementById('riskIndicator');
    const riskLevel = document.getElementById('riskLevel');
    const riskPercentage = document.getElementById('riskPercentage');
    const predictionText = document.getElementById('predictionText');

    riskIndicator.className = `risk-indicator ${results.risk_class}`;
    riskLevel.innerHTML = `<i class="fas fa-shield-alt"></i> ${results.risk_level}`;
    riskPercentage.textContent = `${results.probability}%`;
    predictionText.textContent = results.prediction;

    // Show recommendations
    const recommendationsDiv = document.getElementById('recommendations');
    const recommendationsList = document.getElementById('recommendationsList');

    recommendationsList.innerHTML = '';
    results.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.textContent = rec;
        recommendationsList.appendChild(li);
    });

    recommendationsDiv.style.display = 'block';

    // Create risk chart
    createRiskChart(results);

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';

    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
    });
}

// Create risk visualization chart
function createRiskChart(results) {
    const ctx = document.getElementById('riskChart').getContext('2d');

    // Destroy existing chart if it exists
    if (riskChart) {
        riskChart.destroy();
    }

    const riskFactors = ['Low Risk', 'Moderate Risk', 'High Risk'];
    const riskValues = [
        results.probability < 30 ? results.probability : 0,
        results.probability >= 30 && results.probability < 60 ? results.probability : 0,
        results.probability >= 60 ? results.probability : 0
    ];

    riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: riskFactors,
            datasets: [{
                data: riskValues.length === 3 && riskValues.every(v => v === 0) ?
                    [results.probability < 30 ? 100 : 0,
                    results.probability >= 30 && results.probability < 60 ? 100 : 0,
                    results.probability >= 60 ? 100 : 0] : [30, 30, 40],
                backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                },
                title: {
                    display: true,
                    text: 'Risk Assessment Overview',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                }
            }
        }
    });
}

// Update doctor dashboard
function updateDoctorDashboard() {
    const assessments = allAssessments;
    const appointments = allAppointments;

    // Update stats
    const totalPatients = assessments.length;
    const todayAssessments = assessments.filter(a => a.date === new Date().toLocaleDateString()).length;
    const todayAppointments = appointments.filter(a => a.date === new Date().toISOString().split('T')[0]).length;
    const avgRisk = assessments.length > 0 ?
        Math.round(assessments.reduce((sum, a) => sum + a.results.probability, 0) / assessments.length) : 0;

    document.getElementById('totalPatients').textContent = totalPatients;
    document.getElementById('todayAssessments').textContent = todayAssessments;
    document.getElementById('todayAppointments').textContent = todayAppointments;
    document.getElementById('avgRisk').textContent = avgRisk + '%';

    // Update navigation badges
    document.getElementById('totalPatientsNav').textContent = totalPatients;
    document.getElementById('totalAppointmentsNav').textContent = appointments.length;

    // Create trend chart
    createTrendChart(assessments);
}

// Create trend chart for dashboard
function createTrendChart(assessments) {
    const ctx = document.getElementById('trendChart').getContext('2d');

    if (trendChart) {
        trendChart.destroy();
    }

    // Group assessments by date
    const dateGroups = {};
    assessments.forEach(assessment => {
        const date = assessment.date;
        if (!dateGroups[date]) {
            dateGroups[date] = { low: 0, moderate: 0, high: 0 };
        }

        if (assessment.results.riskLevel === 'Low Risk') {
            dateGroups[date].low++;
        } else if (assessment.results.riskLevel === 'Moderate Risk') {
            dateGroups[date].moderate++;
        } else {
            dateGroups[date].high++;
        }
    });

    const dates = Object.keys(dateGroups).sort();
    const lowRiskData = dates.map(date => dateGroups[date].low);
    const moderateRiskData = dates.map(date => dateGroups[date].moderate);
    const highRiskData = dates.map(date => dateGroups[date].high);

    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Low Risk',
                    data: lowRiskData,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'Moderate Risk',
                    data: moderateRiskData,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    fill: false,
                    tension: 0.1
                },
                {
                    label: 'High Risk',
                    data: highRiskData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    fill: false,
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Risk Assessment Trends Over Time'
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Patients'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

// Populate patients table
function populatePatientsTable() {
    const tbody = document.getElementById('patientsTableBody');
    const assessments = allAssessments;

    if (assessments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 40px; color: #6c757d;">No patient data available</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    assessments.forEach(assessment => {
        const row = document.createElement('tr');
        const riskClass = assessment.results.riskLevel.toLowerCase().replace(' ', '-');

        row.innerHTML = `
                    <td style="font-weight: 600;">${assessment.patientInfo.name}</td>
                    <td>${assessment.patientInfo.age}</td>
                    <td>${assessment.patientInfo.gender}</td>
                    <td>${assessment.patientInfo.contact}</td>
                    <td><span class="risk-badge ${riskClass}">${assessment.results.riskLevel}</span></td>
                    <td>${assessment.healthData.gfr || 'N/A'}</td>
                    <td>${assessment.healthData.serum_creatinine || 'N/A'}</td>
                    <td>${assessment.date}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn view" onclick="viewPatientDetails('${assessment.id}')">
                                <i class="fas fa-eye"></i> View
                            </button>
                            <button class="action-btn edit" onclick="editPatient('${assessment.id}')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="action-btn delete" onclick="deletePatient('${assessment.id}')">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </td>
                `;
        tbody.appendChild(row);
    });
}

// Edit patient function
function editPatient(patientId) {
    const patient = allAssessments.find(a => a.id == patientId);
    if (!patient) return;

    alert(`Editing patient: ${patient.patientInfo.name}\n\nThis would open an edit form in a real application.`);
}

// Delete patient function
function deletePatient(patientId) {
    if (confirm('Are you sure you want to delete this patient record?')) {
        allAssessments = allAssessments.filter(a => a.id != patientId);
        populatePatientsTable();
        updateDoctorDashboard();
        alert('Patient record deleted successfully!');
    }
}

// Update analytics
function updateAnalytics() {
    const assessments = allAssessments;

    const lowRiskCount = assessments.filter(a => a.results.riskLevel === 'Low Risk').length;
    const moderateRiskCount = assessments.filter(a => a.results.riskLevel === 'Moderate Risk').length;
    const highRiskCount = assessments.filter(a => a.results.riskLevel === 'High Risk').length;

    const totalCount = assessments.length;

    document.getElementById('lowRiskCount').textContent = lowRiskCount;
    document.getElementById('moderateRiskCount').textContent = moderateRiskCount;
    document.getElementById('highRiskCount').textContent = highRiskCount;

    document.getElementById('lowRiskPercentage').textContent = totalCount > 0 ? Math.round((lowRiskCount / totalCount) * 100) + '%' : '0%';
    document.getElementById('moderateRiskPercentage').textContent = totalCount > 0 ? Math.round((moderateRiskCount / totalCount) * 100) + '%' : '0%';
    document.getElementById('highRiskPercentage').textContent = totalCount > 0 ? Math.round((highRiskCount / totalCount) * 100) + '%' : '0%';

    // Create analytics chart
    createAnalyticsChart(lowRiskCount, moderateRiskCount, highRiskCount);
}

// Create analytics chart
function createAnalyticsChart(lowRisk, moderateRisk, highRisk) {
    const ctx = document.getElementById('analyticsChart').getContext('2d');

    if (analyticsChart) {
        analyticsChart.destroy();
    }

    analyticsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Low Risk', 'Moderate Risk', 'High Risk'],
            datasets: [{
                label: 'Number of Patients',
                data: [lowRisk, moderateRisk, highRisk],
                backgroundColor: ['#22c55e', '#f59e0b', '#ef4444'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Risk Level Distribution'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Patients'
                    }
                }
            }
        }
    });
}

// View patient details (placeholder function)
function viewPatientDetails(patientId) {
    const patient = allAssessments.find(a => a.id == patientId);
    if (!patient) return;

    alert(`Viewing details for: ${patient.patientInfo.name}\n\nAge: ${patient.patientInfo.age}\nGender: ${patient.patientInfo.gender}\nRisk Level: ${patient.results.riskLevel}\n\nThis would open a detailed patient view in a real application.`);
}

// Filter functionality for patients table
document.getElementById('applyFilters').addEventListener('click', function () {
    const searchTerm = document.getElementById('patientSearch').value.toLowerCase();
    const riskFilter = document.getElementById('riskFilter').value;
    const genderFilter = document.getElementById('genderFilter').value;

    const assessments = allAssessments;

    const filteredAssessments = assessments.filter(assessment => {
        const matchesSearch = !searchTerm ||
            assessment.patientInfo.name.toLowerCase().includes(searchTerm) ||
            assessment.patientInfo.contact.includes(searchTerm);

        const matchesRisk = riskFilter === 'all' ||
            assessment.results.riskLevel.toLowerCase().includes(riskFilter);

        const matchesGender = genderFilter === 'all' ||
            assessment.patientInfo.gender.toLowerCase() === genderFilter;

        return matchesSearch && matchesRisk && matchesGender;
    });

    // Update table with filtered results
    updatePatientsTableWithData(filteredAssessments);
});

// Update patients table with specific data
function updatePatientsTableWithData(assessments) {
    const tbody = document.getElementById('patientsTableBody');

    if (assessments.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 40px; color: #6c757d;">No patients match the selected filters</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    assessments.forEach(assessment => {
        const row = document.createElement('tr');
        const riskClass = assessment.results.riskLevel.toLowerCase().replace(' ', '-');

        row.innerHTML = `
                    <td style="font-weight: 600;">${assessment.patientInfo.name}</td>
                    <td>${assessment.patientInfo.age}</td>
                    <td>${assessment.patientInfo.gender}</td>
                    <td>${assessment.patientInfo.contact}</td>
                    <td><span class="risk-badge ${riskClass}">${assessment.results.riskLevel}</span></td>
                    <td>${assessment.healthData.gfr || 'N/A'}</td>
                    <td>${assessment.healthData.serum_creatinine || 'N/A'}</td>
                    <td>${assessment.date}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn view" onclick="viewPatientDetails('${assessment.id}')">
                                <i class="fas fa-eye"></i> View
                            </button>
                            <button class="action-btn edit" onclick="editPatient('${assessment.id}')">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="action-btn delete" onclick="deletePatient('${assessment.id}')">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                        </div>
                    </td>
                `;
        tbody.appendChild(row);
    });
}

// Global search functionality
document.getElementById('globalSearch').addEventListener('input', function (e) {
    const searchTerm = e.target.value.toLowerCase();
    if (searchTerm.length > 2) {
        // Implement global search logic here
        console.log('Searching for:', searchTerm);
    }
});

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', function () {
    initializeData();
    initializeDiseaseSelection();
    updateDoctorDashboard();

    // Add back button to sidebar (at the bottom)
    addBackButtonToSidebar();

    // Set minimum date for appointment scheduling to today
    const today = new Date().toISOString().split('T')[0];
    if (document.getElementById('appointmentDate')) {
        document.getElementById('appointmentDate').min = today;
    }
});
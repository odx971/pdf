const { PDFDocument } = PDFLib;
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

let currentTheme = localStorage.getItem('theme') || 'dark';
let currentSection = 'merge';

const mergeFiles = [];
const img2pdfFiles = [];
let splitPdfDoc = null;
let splitPages = [];
let unlockPdfBytes = null;
let pdf2imgPdfBytes = null;

document.addEventListener('DOMContentLoaded', init);

function init() {
    applyTheme();
    setupNavigation();
    setupThemeToggle();
    setupMerge();
    setupSplit();
    setupUnlock();
    setupPdf2Img();
    setupImg2Pdf();
    setupDragAndDrop();

    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('sw.js').catch(() => {});
    }
}

function applyTheme() {
    document.documentElement.setAttribute('data-theme', currentTheme);
    const icon = document.querySelector('.theme-icon');
    icon.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
}

function setupThemeToggle() {
    document.getElementById('themeToggle').addEventListener('click', () => {
        currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', currentTheme);
        applyTheme();
    });
}

function setupNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            switchSection(section);
        });
    });
}

function switchSection(section) {
    currentSection = section;
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.querySelector(`[data-section="${section}"]`).classList.add('active');
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.getElementById(section + 'Section').classList.add('active');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

function showLoading(text = 'Processing...') {
    document.getElementById('loadingText').textContent = text;
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / 1048576).toFixed(1) + ' MB';
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

function setupDragAndDrop() {
    document.querySelectorAll('.drop-zone').forEach(zone => {
        zone.addEventListener('dragover', e => {
            e.preventDefault();
            zone.classList.add('dragover');
        });
        zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
        zone.addEventListener('drop', e => {
            e.preventDefault();
            zone.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files);
            handleDroppedFiles(files);
        });
    });
}

function handleDroppedFiles(files) {
    const section = currentSection;
    if (section === 'merge') {
        const pdfs = files.filter(f => f.name.toLowerCase().endsWith('.pdf'));
        pdfs.forEach(f => addMergeFile(f));
    } else if (section === 'split') {
        const pdf = files.find(f => f.name.toLowerCase().endsWith('.pdf'));
        if (pdf) loadSplitPdf(pdf);
    } else if (section === 'unlock') {
        const pdf = files.find(f => f.name.toLowerCase().endsWith('.pdf'));
        if (pdf) loadUnlockPdf(pdf);
    } else if (section === 'pdf2img') {
        const pdf = files.find(f => f.name.toLowerCase().endsWith('.pdf'));
        if (pdf) loadPdf2Img(pdf);
    } else if (section === 'img2pdf') {
        const imgs = files.filter(f => f.type.startsWith('image/'));
        imgs.forEach(f => addImg2PdfFile(f));
    }
}

function setupMerge() {
    const dropZone = document.getElementById('mergeDropZone');
    const fileInput = document.getElementById('mergeFileInput');
    const mergeBtn = document.getElementById('mergeBtn');
    const clearBtn = document.getElementById('mergeClearBtn');

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', e => {
        Array.from(e.target.files).forEach(f => addMergeFile(f));
        fileInput.value = '';
    });

    clearBtn.addEventListener('click', () => {
        mergeFiles.length = 0;
        renderMergeList();
    });

    mergeBtn.addEventListener('click', mergePdf);
}

function addMergeFile(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showToast('Please select PDF files', 'warning');
        return;
    }
    mergeFiles.push({ file, name: file.name, size: file.size });
    renderMergeList();
}

function renderMergeList() {
    const list = document.getElementById('mergeFileList');
    const mergeBtn = document.getElementById('mergeBtn');
    const clearBtn = document.getElementById('mergeClearBtn');

    if (mergeFiles.length === 0) {
        list.innerHTML = '';
        mergeBtn.disabled = true;
        clearBtn.disabled = true;
        return;
    }

    mergeBtn.disabled = false;
    clearBtn.disabled = false;

    list.innerHTML = mergeFiles.map((item, i) => `
        <div class="file-item" draggable="true" data-index="${i}">
            <span class="drag-handle">⋮⋮</span>
            <span class="file-icon">📄</span>
            <div class="file-details">
                <span class="file-name">${item.name}</span>
                <span class="file-meta">${formatSize(item.size)}</span>
            </div>
            <button class="file-remove" data-index="${i}">✕</button>
        </div>
    `).join('');

    list.querySelectorAll('.file-remove').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            mergeFiles.splice(parseInt(btn.dataset.index), 1);
            renderMergeList();
        });
    });

    let dragIndex = null;
    list.querySelectorAll('.file-item').forEach(item => {
        item.addEventListener('dragstart', e => {
            dragIndex = parseInt(item.dataset.index);
            item.classList.add('dragging');
        });
        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
        });
        item.addEventListener('dragover', e => {
            e.preventDefault();
        });
        item.addEventListener('drop', e => {
            e.preventDefault();
            const dropIndex = parseInt(item.dataset.index);
            if (dragIndex !== null && dragIndex !== dropIndex) {
                const moved = mergeFiles.splice(dragIndex, 1)[0];
                mergeFiles.splice(dropIndex, 0, moved);
                renderMergeList();
            }
            dragIndex = null;
        });
    });
}

async function mergePdf() {
    if (mergeFiles.length === 0) return;

    showLoading('Merging PDFs...');
    try {
        const mergedPdf = await PDFDocument.create();

        for (const item of mergeFiles) {
            const bytes = await item.file.arrayBuffer();
            const pdf = await PDFDocument.load(bytes);
            const pages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
            pages.forEach(page => mergedPdf.addPage(page));
        }

        const pdfBytes = await mergedPdf.save();
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        downloadBlob(blob, 'merged.pdf');
        showToast('PDFs merged successfully!', 'success');
    } catch (err) {
        showToast('Error merging PDFs: ' + err.message, 'error');
    }
    hideLoading();
}

function setupSplit() {
    const dropZone = document.getElementById('splitDropZone');
    const fileInput = document.getElementById('splitFileInput');
    const selectAllBtn = document.getElementById('splitSelectAll');
    const extractBtn = document.getElementById('splitExtractBtn');

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', e => {
        if (e.target.files[0]) loadSplitPdf(e.target.files[0]);
        fileInput.value = '';
    });

    selectAllBtn.addEventListener('click', () => {
        const allSelected = splitPages.every(p => p.selected);
        splitPages.forEach(p => p.selected = !allSelected);
        renderSplitPages();
    });

    extractBtn.addEventListener('click', extractSplitPages);
}

async function loadSplitPdf(file) {
    showLoading('Loading PDF...');
    try {
        const bytes = await file.arrayBuffer();
        splitPdfDoc = await PDFDocument.load(bytes);
        const pageCount = splitPdfDoc.getPageCount();

        splitPages = [];
        for (let i = 0; i < pageCount; i++) {
            splitPages.push({ index: i, selected: true });
        }

        const dropZone = document.getElementById('splitDropZone');
        dropZone.innerHTML = `
            <div class="drop-icon">📄</div>
            <p>${file.name}</p>
            <p class="drop-hint">${pageCount} pages - tap pages to select</p>
        `;

        await renderSplitPages();
        document.getElementById('splitSelectAll').disabled = false;
        document.getElementById('splitExtractBtn').disabled = false;
    } catch (err) {
        showToast('Error loading PDF: ' + err.message, 'error');
    }
    hideLoading();
}

async function renderSplitPages() {
    const grid = document.getElementById('splitPageGrid');
    grid.innerHTML = '';

    const tempDoc = await PDFDocument.create();
    const srcBytes = await splitPdfDoc.save();
    const srcDoc = await PDFDocument.load(srcBytes);

    for (const page of splitPages) {
        const [copiedPage] = await tempDoc.copyPages(srcDoc, [page.index]);
        tempDoc.addPage(copiedPage);

        const card = document.createElement('div');
        card.className = `page-card ${page.selected ? 'selected' : ''}`;
        card.dataset.index = page.index;

        const canvas = document.createElement('canvas');
        const previewDoc = await PDFDocument.create();
        const [p] = await previewDoc.copyPages(srcDoc, [page.index]);
        previewDoc.addPage(p);
        const previewBytes = await previewDoc.save();

        const pdfDoc = await pdfjsLib.getDocument({ data: previewBytes }).promise;
        const pdfPage = await pdfDoc.getPage(1);
        const viewport = pdfPage.getViewport({ scale: 0.5 });
        canvas.width = viewport.width;
        canvas.height = viewport.height;

        const ctx = canvas.getContext('2d');
        await pdfPage.render({ canvasContext: ctx, viewport }).promise;

        card.innerHTML = `
            <div class="page-checkbox">✓</div>
            <span class="page-number">Page ${page.index + 1}</span>
        `;
        card.prepend(canvas);

        card.addEventListener('click', () => {
            page.selected = !page.selected;
            card.classList.toggle('selected');
            updateSplitSelectAll();
        });

        grid.appendChild(card);
    }

    tempDoc.destroy();
}

function updateSplitSelectAll() {
    const allSelected = splitPages.every(p => p.selected);
    document.getElementById('splitSelectAll').textContent = allSelected ? 'Deselect All' : 'Select All';
}

async function extractSplitPages() {
    const selected = splitPages.filter(p => p.selected);
    if (selected.length === 0) {
        showToast('Please select at least one page', 'warning');
        return;
    }

    showLoading('Extracting pages...');
    try {
        const newPdf = await PDFDocument.create();
        const srcBytes = await splitPdfDoc.save();
        const srcDoc = await PDFDocument.load(srcBytes);

        const indices = selected.map(p => p.index);
        const pages = await newPdf.copyPages(srcDoc, indices);
        pages.forEach(page => newPdf.addPage(page));

        const pdfBytes = await newPdf.save();
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        downloadBlob(blob, 'extracted.pdf');
        showToast(`Extracted ${selected.length} pages!`, 'success');
    } catch (err) {
        showToast('Error extracting pages: ' + err.message, 'error');
    }
    hideLoading();
}

function setupUnlock() {
    const dropZone = document.getElementById('unlockDropZone');
    const fileInput = document.getElementById('unlockFileInput');
    const unlockBtn = document.getElementById('unlockBtn');
    const togglePwBtn = document.getElementById('togglePasswordBtn');

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', e => {
        if (e.target.files[0]) loadUnlockPdf(e.target.files[0]);
        fileInput.value = '';
    });

    togglePwBtn.addEventListener('click', () => {
        const input = document.getElementById('unlockPassword');
        input.type = input.type === 'password' ? 'text' : 'password';
    });

    unlockBtn.addEventListener('click', unlockPdf);
}

async function loadUnlockPdf(file) {
    try {
        unlockPdfBytes = await file.arrayBuffer();
        const pdfDoc = await PDFDocument.load(unlockPdfBytes, { ignoreEncryption: true });

        document.getElementById('unlockDropZone').classList.add('hidden');
        document.getElementById('unlockFileInfo').classList.remove('hidden');
        document.getElementById('unlockFileName').textContent = file.name;

        const statusEl = document.getElementById('unlockFileStatus');
        try {
            await PDFDocument.load(unlockPdfBytes);
            statusEl.textContent = 'Not encrypted';
            statusEl.className = 'file-status unlocked';
        } catch (e) {
            if (e.message.includes('password')) {
                statusEl.textContent = 'Password protected';
                statusEl.className = 'file-status locked';
                document.getElementById('unlockBtn').disabled = false;
            } else {
                statusEl.textContent = 'Not encrypted';
                statusEl.className = 'file-status unlocked';
            }
        }
    } catch (err) {
        showToast('Error loading PDF: ' + err.message, 'error');
    }
}

async function unlockPdf() {
    const password = document.getElementById('unlockPassword').value;
    if (!password) {
        showToast('Please enter the password', 'warning');
        return;
    }

    showLoading('Removing password...');
    try {
        const pdfDoc = await PDFDocument.load(unlockPdfBytes, { password });
        const pdfBytes = await pdfDoc.save();
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        downloadBlob(blob, 'unlocked.pdf');
        showToast('Password removed successfully!', 'success');
    } catch (err) {
        showToast('Wrong password or error: ' + err.message, 'error');
    }
    hideLoading();
}

function setupPdf2Img() {
    const dropZone = document.getElementById('pdf2imgDropZone');
    const fileInput = document.getElementById('pdf2imgFileInput');
    const convertBtn = document.getElementById('pdf2imgBtn');

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', e => {
        if (e.target.files[0]) loadPdf2Img(e.target.files[0]);
        fileInput.value = '';
    });

    convertBtn.addEventListener('click', convertPdfToImages);
}

async function loadPdf2Img(file) {
    showLoading('Loading PDF...');
    try {
        pdf2imgPdfBytes = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument({ data: pdf2imgPdfBytes.slice(0) }).promise;
        const pagesContainer = document.getElementById('pdf2imgPages');
        pagesContainer.innerHTML = '';

        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const viewport = page.getViewport({ scale: 0.3 });
            const canvas = document.createElement('canvas');
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            const ctx = canvas.getContext('2d');
            await page.render({ canvasContext: ctx, viewport }).promise;
            pagesContainer.appendChild(canvas);
        }

        document.getElementById('pdf2imgDropZone').classList.add('hidden');
        document.getElementById('pdf2imgPreview').classList.remove('hidden');
        document.getElementById('pdf2imgBtn').disabled = false;
    } catch (err) {
        showToast('Error loading PDF: ' + err.message, 'error');
    }
    hideLoading();
}

async function convertPdfToImages() {
    if (!pdf2imgPdfBytes) return;

    const format = document.getElementById('imgFormat').value;
    const quality = parseFloat(document.getElementById('imgQuality').value);

    showLoading('Converting to images...');
    try {
        const pdf = await pdfjsLib.getDocument({ data: pdf2imgPdfBytes.slice(0) }).promise;

        if (pdf.numPages === 1) {
            const page = await pdf.getPage(1);
            const viewport = page.getViewport({ scale: 2 });
            const canvas = document.createElement('canvas');
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            const ctx = canvas.getContext('2d');
            await page.render({ canvasContext: ctx, viewport }).promise;

            canvas.toBlob(blob => {
                downloadBlob(blob, `page_1.${format === 'jpeg' ? 'jpg' : format}`);
                showToast('Image saved!', 'success');
            }, `image/${format}`, quality);
        } else {
            const zip = new JSZip();
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const viewport = page.getViewport({ scale: 2 });
                const canvas = document.createElement('canvas');
                canvas.width = viewport.width;
                canvas.height = viewport.height;
                const ctx = canvas.getContext('2d');
                await page.render({ canvasContext: ctx, viewport }).promise;

                const dataUrl = canvas.toDataURL(`image/${format}`, quality);
                const base64 = dataUrl.split(',')[1];
                zip.file(`page_${i}.${format === 'jpeg' ? 'jpg' : format}`, base64, { base64: true });
            }

            const content = await zip.generateAsync({ type: 'blob' });
            downloadBlob(content, 'pages.zip');
            showToast('Images saved as ZIP!', 'success');
        }
    } catch (err) {
        showToast('Error converting: ' + err.message, 'error');
    }
    hideLoading();
}

function setupImg2Pdf() {
    const dropZone = document.getElementById('img2pdfDropZone');
    const fileInput = document.getElementById('img2pdfFileInput');
    const createBtn = document.getElementById('img2pdfBtn');
    const clearBtn = document.getElementById('img2pdfClearBtn');

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', e => {
        Array.from(e.target.files).forEach(f => addImg2PdfFile(f));
        fileInput.value = '';
    });

    clearBtn.addEventListener('click', () => {
        img2pdfFiles.length = 0;
        renderImg2PdfList();
    });

    createBtn.addEventListener('click', createPdfFromImages);
}

function addImg2PdfFile(file) {
    if (!file.type.startsWith('image/')) {
        showToast('Please select image files', 'warning');
        return;
    }
    img2pdfFiles.push({ file, name: file.name, size: file.size });
    renderImg2PdfList();
}

function renderImg2PdfList() {
    const list = document.getElementById('img2pdfFileList');
    const createBtn = document.getElementById('img2pdfBtn');
    const clearBtn = document.getElementById('img2pdfClearBtn');

    if (img2pdfFiles.length === 0) {
        list.innerHTML = '';
        createBtn.disabled = true;
        clearBtn.disabled = true;
        return;
    }

    createBtn.disabled = false;
    clearBtn.disabled = false;

    list.innerHTML = img2pdfFiles.map((item, i) => `
        <div class="file-item" draggable="true" data-index="${i}">
            <span class="drag-handle">⋮⋮</span>
            <span class="file-icon">🖼️</span>
            <div class="file-details">
                <span class="file-name">${item.name}</span>
                <span class="file-meta">${formatSize(item.size)}</span>
            </div>
            <button class="file-remove" data-index="${i}">✕</button>
        </div>
    `).join('');

    list.querySelectorAll('.file-remove').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            img2pdfFiles.splice(parseInt(btn.dataset.index), 1);
            renderImg2PdfList();
        });
    });

    let dragIndex = null;
    list.querySelectorAll('.file-item').forEach(item => {
        item.addEventListener('dragstart', () => {
            dragIndex = parseInt(item.dataset.index);
            item.classList.add('dragging');
        });
        item.addEventListener('dragend', () => {
            item.classList.remove('dragging');
        });
        item.addEventListener('dragover', e => e.preventDefault());
        item.addEventListener('drop', e => {
            e.preventDefault();
            const dropIndex = parseInt(item.dataset.index);
            if (dragIndex !== null && dragIndex !== dropIndex) {
                const moved = img2pdfFiles.splice(dragIndex, 1)[0];
                img2pdfFiles.splice(dropIndex, 0, moved);
                renderImg2PdfList();
            }
            dragIndex = null;
        });
    });
}

async function createPdfFromImages() {
    if (img2pdfFiles.length === 0) return;

    showLoading('Creating PDF...');
    try {
        const pdf = await PDFDocument.create();

        for (const item of img2pdfFiles) {
            const bytes = await item.file.arrayBuffer();
            let image;
            if (item.file.type === 'image/png') {
                image = await pdf.embedPng(bytes);
            } else {
                image = await pdf.embedJpg(bytes);
            }

            const page = pdf.addPage([image.width, image.height]);
            page.drawImage(image, {
                x: 0,
                y: 0,
                width: image.width,
                height: image.height
            });
        }

        const pdfBytes = await pdf.save();
        const blob = new Blob([pdfBytes], { type: 'application/pdf' });
        downloadBlob(blob, 'images.pdf');
        showToast('PDF created successfully!', 'success');
    } catch (err) {
        showToast('Error creating PDF: ' + err.message, 'error');
    }
    hideLoading();
}

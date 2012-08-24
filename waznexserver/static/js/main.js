function adjustRatio(img) {
    if(window.innerHeight < img.height) {
        img.style.height = '100%';
        img.style.width = 'auto';
    }
    else if(window.innerWidth < img.width) {
        img.style.width = '100%';
        img.style.height = 'auto';
    }
}
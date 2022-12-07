

  var currentTab = 0; // Current tab is set to be the first tab (0)
    showTab(currentTab); // Display the current tab
    function showTab(n) {
      var x = document.getElementsByClassName("tab");
      x[n].style.display = "block";
      if(n == 0){
        document.getElementById("prevBtn").style.display = "none";
        document.getElementById("nextBtn").style.display = "none";
      } else {
        document.getElementById("prevBtn").style.display = "inline";
        document.getElementById("nextBtn").style.display = "inline";
      }
      if (n == (x.length - 1 )){
        document.getElementById("nextBtn").style.display = "none";
        document.getElementById("SubmitBtn").style.display = "inline";
      } else {
        document.getElementById("SubmitBtn").style.display = "none";
      }
      
      
    }

  function btnEvent  (n) {
    var x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "none" ;
    currentTab = currentTab + n;
    if(currentTab >= x.length){
      document.getElementById("regForm").submit();
      return false;
    }
    showTab(currentTab)
  }
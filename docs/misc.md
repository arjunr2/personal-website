## Under Construction

<a class="collapsible"> ## Curriculum Vitae
</a>

<div class="content">
<p align="center">
<iframe src="../assets/CV_Work.pdf" width="90%" height=830> </iframe>
</p>
</div>

<style>
  .md-typeset h2 {
    display: none;
  }
</style>


<style>
a {
  cursor: pointer;
}
</style>

<body>
<a class="collapsible"> 
Curriculum Vitae
</a>

<div class="content">
<p align="center">
<iframe src="../assets/CV_Work.pdf" width="90%" height=830> </iframe>
</p>
</div>

<a class="collapsible"> 
  <h2> Curriculum Vitae 2 </h2>
</a>

<div class="content">
<p align="center">
<iframe src="../assets/CV_Work.pdf" width="90%" height=830> </iframe>
</p>
</div>

<script>
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("passive");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}
</script>
</body>

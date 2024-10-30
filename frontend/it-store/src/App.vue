<script>
export default{
    data(){
        return{
            info: 'Title'
        }
    }

}
</script>

<template>
<h1>{{info}}</h1>

<p>It's a store</p>
</template>

<style scoped>

h1 {
    color: blue;
    font-weight: 500;
    font-size: 2.6rem;
    top: -10px;
    
}

p {
    font-size: 1.2rem;
    color:rgb(1,1,1);
}

</style>

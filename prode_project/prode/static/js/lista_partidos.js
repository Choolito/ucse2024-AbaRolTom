function cambiarFecha(fecha) {
    fecha = parseInt(fecha);
    if (fecha < 0) {
        fecha = 0;
    } else if (fecha > 27) {
        fecha = 27;
    }
    if (fecha === 0) {
        window.location.href = '{% url "lista_partidos" %}';
    } else {
        window.location.href = `?fecha_liga=${fecha}`;
    }
}
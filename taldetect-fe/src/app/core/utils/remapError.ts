export const mapError = (error: any) => {
    switch (error) {
        case "Unknown Error":
            return "BackEnd Offline";
        default:
            return "Errore Sconosciuto";
    }
}
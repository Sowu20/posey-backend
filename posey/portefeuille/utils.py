STATUT_MAPPING = {
    0: ("succes", "Paiement confirmé."),
    2: ("en attente", "Paiement en cours."),
    4: ("expire", "Paiement expiré."),
    6: ("annule", "Paiement annulé."),
}

def get_statut_message(status_code: int):
    """
    Retourne le statut interne et le message associé à partir du code PayGate.
    """
    return STATUT_MAPPING.get(status_code, ("echec", "Paiement échoué."))
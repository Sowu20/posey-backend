from rest_framework import serializers
from portefeuille.models import Portefeuille, Transaction

class PortefeuilleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portefeuille
        fields = ['solde', 'date_mise_a_jour']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class ListeTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['methode_payement', 'montant', 'statut', 'date_transaction', 'tx_reference']

class ListeTransactionStatutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['methode_payement', 'statut', 'date_transaction', 'tx_reference']